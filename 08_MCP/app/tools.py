import time
from datetime import datetime

import secrets

from mcp.server.auth.middleware.auth_context import get_access_token

from .server import mcp, oauth_provider


async def _get_username() -> str:
    token = get_access_token()
    if token is None:
        raise ValueError("Not authenticated")
    username = await oauth_provider.get_username_for_token(token.token)
    if username is None:
        raise ValueError("User not found for token")
    return username


@mcp.tool()
async def list_products(category: str | None = None) -> list[dict]:
    """Browse the cat shop catalog. Optionally filter by category (toys, beds, food, furniture)."""
    db = await oauth_provider._get_db()
    if category:
        cursor = await db.execute(
            "SELECT id, name, description, price, category FROM products WHERE category = ?",
            (category,),
        )
    else:
        cursor = await db.execute(
            "SELECT id, name, description, price, category FROM products"
        )
    rows = await cursor.fetchall()
    return [
        {"id": r[0], "name": r[1], "description": r[2], "price": r[3], "category": r[4]}
        for r in rows
    ]


@mcp.tool()
async def get_product(product_id: int) -> dict:
    """Get full details of a single product by its ID."""
    db = await oauth_provider._get_db()
    cursor = await db.execute(
        "SELECT id, name, description, price, category FROM products WHERE id = ?",
        (product_id,),
    )
    row = await cursor.fetchone()
    if row is None:
        return {"error": "Product not found"}
    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "price": row[3],
        "category": row[4],
    }


@mcp.tool()
async def add_to_cart(product_id: int, quantity: int = 1) -> dict:
    """Add a product to your shopping cart. If already in cart, quantity is increased."""
    username = await _get_username()
    db = await oauth_provider._get_db()

    cursor = await db.execute("SELECT name FROM products WHERE id = ?", (product_id,))
    product = await cursor.fetchone()
    if product is None:
        return {"error": "Product not found"}

    await db.execute(
        """INSERT INTO cart_items (username, product_id, quantity)
           VALUES (?, ?, ?)
           ON CONFLICT(username, product_id)
           DO UPDATE SET quantity = quantity + excluded.quantity""",
        (username, product_id, quantity),
    )
    await db.commit()
    return {"success": True, "message": f"Added {quantity}x {product[0]} to your cart"}


@mcp.tool()
async def view_cart() -> dict:
    """View everything in your shopping cart with quantities and totals."""
    username = await _get_username()
    db = await oauth_provider._get_db()
    cursor = await db.execute(
        """SELECT p.id, p.name, p.price, c.quantity
           FROM cart_items c JOIN products p ON c.product_id = p.id
           WHERE c.username = ?""",
        (username,),
    )
    rows = await cursor.fetchall()
    items = [
        {
            "product_id": r[0],
            "name": r[1],
            "price": r[2],
            "quantity": r[3],
            "subtotal": round(r[2] * r[3], 2),
        }
        for r in rows
    ]
    total = round(sum(i["subtotal"] for i in items), 2)
    return {"items": items, "total": total, "item_count": len(items)}


@mcp.tool()
async def remove_from_cart(product_id: int) -> dict:
    """Remove a product from your shopping cart."""
    username = await _get_username()
    db = await oauth_provider._get_db()
    cursor = await db.execute(
        "DELETE FROM cart_items WHERE username = ? AND product_id = ?",
        (username, product_id),
    )
    await db.commit()
    if cursor.rowcount == 0:
        return {"error": "Item not in cart"}
    return {"success": True, "message": "Item removed from cart"}


@mcp.tool()
async def checkout() -> dict:
    """Complete your purchase. Shows order summary and clears the cart."""
    username = await _get_username()
    db = await oauth_provider._get_db()

    cart = await view_cart()
    if not cart["items"]:
        return {"error": "Your cart is empty"}

    cursor = await db.execute(
        """INSERT INTO orders (username, total, created_at)
            VALUES (?, ?, ?)""",
        (username, cart["total"], time.time()),
    )
    db_order_id = cursor.lastrowid
    
    await db.executemany(
        """INSERT INTO order_items (order_id, product_id, quantity, price) 
            VALUES (?, ?, ?, ?)""",
        [
            (db_order_id, item["product_id"], item["quantity"], item["price"]) 
            for item in cart["items"]
        ]
    )

    await db.execute("DELETE FROM cart_items WHERE username = ?", (username,))
    await db.commit()

    order_id = secrets.token_hex(8).upper()
    return {
        "order_id": order_id,
        "status": "confirmed",
        "items": cart["items"],
        "total": cart["total"],
        "message": f"Order {order_id} confirmed! Thanks {username}, your cats will love their new goodies!",
    }


@mcp.tool()
async def search_products(query: str) -> list[dict]:
    """Search the cat shop catalog by keyword. Matches against product name and description (case-insensitive, partial match)."""
    db = await oauth_provider._get_db()
    cursor = await db.execute(
        "SELECT id, name, description, price, category FROM products WHERE name LIKE '%' || ? || '%' OR description LIKE '%' || ? || '%'",
        (query, query),
    )
    rows = await cursor.fetchall()
    return [
        {"id": r[0], "name": r[1], "description": r[2], "price": r[3], "category": r[4]}
        for r in rows
    ]


@mcp.tool()
async def update_cart_quantity(product_id: int, quantity: int) -> dict:
    """Set a specific quantity for a product already in your cart. Replaces the current quantity. Use this when the user says 'change to X' or 'set quantity to X'."""
    username = await _get_username()
    db = await oauth_provider._get_db()

    cursor = await db.execute("SELECT name FROM products WHERE id = ?", (product_id,))
    product = await cursor.fetchone()
    if product is None:
        return {"error": "Product not found"}

    update_cursor = await db.execute(
        """UPDATE cart_items SET quantity = ? 
           WHERE username = ? AND product_id = ?""", 
        (quantity, username, product_id),
    )
    await db.commit()
    if update_cursor.rowcount == 0:
        return {"error": "Item not in cart"}
    return {"success": True, "message": f"Updated {product[0]} to {quantity} on your cart"}


@mcp.tool()
async def add_to_wishlist(product_id: int) -> dict:
    """Add a product to your wishlist for later reference. If already in wishlist, silently skips."""
    username = await _get_username()
    db = await oauth_provider._get_db()

    cursor = await db.execute("SELECT name FROM products WHERE id = ?", (product_id,))
    product = await cursor.fetchone()
    if product is None:
        return {"error": "Product not found"}

    await db.execute(
        """INSERT INTO wishlist (username, product_id, created_at)
           VALUES (?, ?, ?)
           ON CONFLICT(username, product_id)
           DO NOTHING""",
        (username, product_id, time.time()),
    )
    await db.commit()
    return {"success": True, "message": f"Added {product[0]} to your wishlist"}


@mcp.tool()
async def view_wishlist() -> dict:
    """View everything in your wishlist."""
    username = await _get_username()
    db = await oauth_provider._get_db()
    cursor = await db.execute(
        """SELECT p.id, p.name, w.created_at
           FROM wishlist w JOIN products p ON w.product_id = p.id
           WHERE w.username = ?""",
        (username,),
    )
    rows = await cursor.fetchall()
    items = [
        {
            "product_id": r[0],
            "name": r[1],
            "created_at": r[2],
        }
        for r in rows
    ]
    if len(items) == 0:
        return {"items": [], "message": "Your wishlist is empty"}

    no_of_items = '1 item' if len(items) == 1 else f'{len(items)} items'
    return {"items": items, "message": f"{no_of_items} found in your wishlist!"}


@mcp.tool()
async def get_order_history(number_of_orders: int = 5) -> dict:
    """View your most recent orders with full item details, prices, and totals. Use number_of_orders to control how many past orders to retrieve."""
    username = await _get_username()
    db = await oauth_provider._get_db()

    cursor = await db.execute(
        """SELECT id, total, created_at 
            FROM orders WHERE username = ? 
            ORDER BY created_at DESC LIMIT ?""",
        (username, number_of_orders)
    )
    order_rows = await cursor.fetchall()
    orders = [
        {
            "id": r[0],
            "total": r[1],
            "created_at": r[2],
        }
        for r in order_rows
    ]

    for index, order in enumerate(orders):
        cursor = await db.execute(
            """SELECT oi.product_id, p.name, oi.price, oi.quantity
                FROM order_items oi JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?""",
            (order['id'],),
        )
        order_items = await cursor.fetchall()
        orders[index]['items'] = [
            {
                "product_id": item[0],
                "name": item[1],
                "price": item[2],
                "quantity": item[3],
            }
            for item in order_items
        ]
    if len(orders) == 0:
        return {"history": [], "message": "No order history found"}
    return {"history": orders, "message": f"The history for your last {len(orders)} orders retrieved!"}


@mcp.tool()
async def get_order_statistics(months: int = 4) -> dict:
    """View purchase statistics for the last N months, including total orders, total spent, average order value, spending breakdown by category, top purchased products, and monthly spending trend.
       ... Returns spending by category (suitable for a pie chart), top products by order count (suitable for a horizontal bar chart), and monthly spending trend (suitable for a line chart).
    """
    username = await _get_username()
    db = await oauth_provider._get_db()
    cutoff = time.time() - (months * 30 * 24 * 60 * 60)

    cursor = await db.execute(
        """SELECT COUNT(*), SUM(total), AVG(total), MIN(created_at)
            FROM orders WHERE username = ? AND created_at >= ?""",
        (username, cutoff)
    )
    overall_numbers = await cursor.fetchone()

    if not overall_numbers[0]:
        return {"statistics": None, "message": f"No orders found in the last {months} months"}


    cursor = await db.execute(
            """SELECT p.category, ROUND(SUM(oi.price * oi.quantity), 2) as amount
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                JOIN orders o ON oi.order_id = o.id
                WHERE o.username = ? AND o.created_at >= ?
                GROUP BY p.category
                ORDER BY amount DESC""",
            (username, cutoff)
        )
    spending_by_category = await cursor.fetchall()

    cursor = await db.execute(
        """SELECT p.name, COUNT(oi.order_id) as order_count, ROUND(SUM(oi.price * oi.quantity), 2) as total_spent
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.username = ? AND o.created_at >= ?
            GROUP BY p.id, p.name
            ORDER BY order_count DESC
            LIMIT 5""",
        (username, cutoff)
    )
    top_products = await cursor.fetchall()

    cursor = await db.execute(
        """SELECT strftime('%Y-%m', datetime(created_at, 'unixepoch')) as month,
            ROUND(SUM(total), 2) as amount
            FROM orders
            WHERE username = ? AND created_at >= ?
            GROUP BY month
            ORDER BY month""",
        (username, cutoff)
    )
    monthly_spend = await cursor.fetchall()

    return {
        "statistics": {
            'overall_numbers': {
                "total_orders": overall_numbers[0],
                "total_spent": overall_numbers[1],
                "avg_order_value": overall_numbers[2],
                "first_order_date": datetime.fromtimestamp(overall_numbers[3]).strftime('%Y-%m-%d') if overall_numbers[3] else None,

            },
            "spending_by_category": [
                {
                    "category": row[0],
                    "amount": row[1],
                }
                for row in spending_by_category
            ],
            "top_products": [
                {
                    "name": row[0],
                    "order_count": row[1],
                    "total_spent": row[2],
                }

                for row in top_products
            ],
            "monthly_spend": [
                {
                    "month": row[0],
                    "amount": row[1]
                }
                for row in monthly_spend
            ]
        }
    }

