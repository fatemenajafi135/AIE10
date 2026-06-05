<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 1: Dense Vector Retrieval</h1>

### [Quicklinks]()

| 📰 Module Sheet                                                                 | ⏺️ Recording | 🖼️ Slides | 👨‍💻 Repo       | 📝 Homework | 📁 Feedback |
| :------------------------------------------------------------------------------- | :----------- | :-------- | :------------ | :---------- | :---------- |
| [Dense Vector Retrieval](../00_Docs/Modules/01_Dense_Vector_Retrieval/README.md) |[Recording!](https://us02web.zoom.us/rec/share/sHWvo0Nd1aI0SEhKecOLEX9kFGVJJAdYfsKiuTmm8t85W48Z2lnjpnzTy8jAd8R5.PwuqibGwAZhvDd8c) <br> passcode: `C62n^@Q!`| [Session 1 Slides](https://canva.link/htfqf8i39yejyhn) | You are here! | [Session 1 Assignment](https://forms.gle/Z9qskfVaAvPjn6gz8) | [Feedback 6/2](https://forms.gle/21a2uoL9DVZPwgJP6) |


## 🏗️ How AIM Does Assignments

> 📅 **Assignments will always be released to students as live class begins.** We will never release assignments early.

Each assignment will have a few of the following categories of exercises:

- ❓ **Questions** - these will be questions that you will be expected to gather the answer to. These can appear as general questions, or questions meant to spark a discussion in your breakout rooms.

- 🏗️ **Activities** - these will be work or coding activities meant to reinforce specific concepts or theory components.

- 🚧 **Advanced Builds (optional)** - Take on a challenge. These builds require you to create something with minimal guidance outside of the documentation.

## Main Assignment

In this assignment, you will build a vector RAG application using LangChain v1, OpenAI embeddings, and Qdrant.

The main notebook is:

```text
01_Cat_Health_Vector_RAG_LangChain_Qdrant.ipynb
```

The notebook uses the bundled cat health guideline PDF in `data/cat_health_guidelines.pdf`.

### Setup

From this folder, install the environment with uv:

```bash
uv sync
```

Then open the notebook in Cursor or VS Code and select the Python/Jupyter environment created by uv.

You will also need an OpenAI API key available when running the notebook.

---

## 🏗️ Activity #1: Embedding Similarity

Run the embedding similarity primer in the notebook.

You will compare embeddings for terms like:

- `king`
- `queen`
- `banana`
- `cat`
- `veterinarian`
- `cat health guidelines`

#### ❓Question #1

Why is cosine similarity useful for dense vector retrieval?

##### ✅ Answer

_In vector retrieval, we care about semantic direction, not magnitude. Cosine similarity measures the angle between two vectors, making it robust to differences in vector magnitude. A short sentence and a long document expressing the same concept will point in the same direction even if their magnitudes differ. Dot product would unfairly favor larger-magnitude vectors. In other words cosine similarity asks "do these vectors point in the same direction?" which maps directly to "do these texts carry the same meaning?"_

_Cosine similarity is also more stable in high-dimensional spaces; where Euclidean distance becomes unreliable due to the curse of dimensionality. Its output is bounded between -1 and 1, making scores comparable across queries without extra normalization._

_Most embedding models are trained with cosine similarity as the optimization objective like contrastive learning, so using it at retrieval time stays consistent with how the embedding space was shaped._

---

## 🏗️ Activity #2: Build the Vector RAG Pipeline

Run the notebook sections that:

1. Load the PDF into LangChain `Document` objects
2. Split the document into chunks
3. Embed the chunks
4. Store the chunk embeddings in in-memory Qdrant
5. Retrieve relevant chunks with similarity scores
6. Generate an answer grounded in retrieved context

#### ❓Question #2

Why is metadata important for a RAG application?

##### ✅ Answer:

_Having metadata in RAG can benefit us in several ways:_
* _Allows us to __pre-filter__ documents or the vector search space before semantic search, which can be costly and noisy and improves retrieval relevancy. It can also serve as a layer of access control._
* _While chunking may lose general context tied to the whole document, metadata __can carry that context forward__ to each chunk._
* _Enables __hybrid search__, combining exact matching with semantic search when both precision and recall matter._
* _Plays a critical role in __evaluation__ for tracing and measuring the retrieval module itself, metadata is a key source for computing faithfulness and context precision_


#### ❓Question #3

What tradeoff do we make when choosing chunk size and chunk overlap?

##### ✅ Answer:

_Both too-small and too-large chunk sizes introduce their own tradeoffs:_

* _Smaller chunks produce more precise retrieval but may lose surrounding context needed to fully answer a query. They also increase storage and retrieval overhead._
* _Larger chunks carry more context per chunk but may introduce noise or irrelevant content that dilutes the embedding._

_For chunk overlap, choosing no overlap risks losing continuity at chunk boundaries, while high overlap introduces redundancy and increases retrieval cost._

_There is no universally optimal strategy and each document type and use case needs its own chunking decision, strategies, tuned and validated against retrieval metrics._


#### ❓Question #4

What does a similarity score help you understand, and what does it not prove by itself?

##### ✅ Answer:

_Embedding vectors are placed in a high-dimensional vector space. The similarity score reflects how geometrically close two vectors are in that space. The higher the score, the more likely the two words, sentences, or documents share similar meaning in natural language. However, this is not guaranteed, because the features captured by an embedding model may not align with how humans interpret language and are not always easily interpretable._

_Additionally, similarity is embedding-model-dependent; So, the same text can produce different scores across different models._

_Another subtle issue: antonyms and opposing concepts often appear close in vector space because they share similar context windows during training. This makes their relationship hard to infer from vectors alone._

_Finally, since we are computing similarity between a query and chunks, a high score does not necessarily mean the chunk is useful or answers the query. It only reflects topical closeness, not answer quality or factual correctness._


---

## 🏗️ Activity #3: Vibe Check Retrieval Quality

Run the notebook's vibe check queries and inspect both:

- The retrieved context
- The generated answer

#### ❓Question #5

For the vibe check queries, did the retrieved context seem relevant before generation? Why or why not?

##### ✅ Answer:

_It seems for each question, the retriever tried to find the most similar chunks existing across all chunks. In detail:_
- __What preventive care is recommended for cats?__ _Scores of retrieved chunks are relatively high, so they are supposed to have a similar context to the question and we expect to find the answer in these chunks. Reviewing them in detail shows that while we get relevant answers in the first and last chunks, the second one is semi-relevant and the third one is bibliography with no actionable preventive care content! It's a common issue because bibliography chunks likely have high semantic overlap but carry zero answerable content._
- __What symptoms should make me call a veterinarian?__ _The first two chunks are completely relevant and cover the whole list of symptoms, the fourth chunk is partially relevant, but the third one is off-topic._
- __What should I know about feeding a healthy adult cat?__ _Scores show high semantic relevancy between the question and chunks, and reviewing the chunks, it seems the best retrieved set among these questions because they are highly relevant and the order is reasonable; the last one is not completely relevant but also not irrelevant._
- __Can my cat help me file my taxes?__ _Reviewing the retrieved chunks, scores are lower than the other questions, signaling weak semantic overlap. Although they might be the most relevant chunks in the whole set, there is no meaningful similarity between the chunks and the question at all. The retriever is forced to return a fixed top-k chunks. So both the retriever and LLM did their job well. This was out-of-domain, and we don't expect cats to do our taxes, but we hope AI agents do :))_

---

## 🏗️ Activity #4: Tune Retrieval

Improve retrieval quality by changing one or more of:

- Chunk size
- Chunk overlap
- Retrieval `k`
- Query wording

Document what changed and whether retrieval improved.

##### Settings Changed:

- chunk_size: 1000 → 1500
- chunk_overlap: 200 → 200 (unchanged)
- k: 4 → 5

##### Results:

1. Increasing chunk_size from 1000 to 1500 had the biggest impact. Larger chunks keep full topical sections intact, so each retrieved unit contains complete guidance rather than a paragraph fragment. This eliminated bibliography noise and surfaced new topics like vaccination protocols and oral health that were split across chunks at smaller sizes.
2. Increasing k from 4 to 5 added one more retrieved chunk without introducing noise, broadening coverage to include life-stage diagnostics and zoonosis prevention alongside the core preventive care sections.
3. Chunk overlap had minimal effect at the 1500-token size. Increasing it from 200 to 300 (Experiment 6) caused slight cross-boundary bleed with no meaningful quality gain, so overlap=200 was kept as the final setting.

---

## Optional Deep Dive: RAG From Scratch

If you want to look underneath the library abstractions, run the optional reference notebook:

```text
02_Cat_Health_Vector_RAG_From_Scratch.ipynb
```

It builds the same retrieval pipeline again with only:

- `pypdf` for extracting text from the PDF
- Python standard-library HTTP requests for calling OpenAI
- Handcrafted document, chunking, embedding, similarity-search, vector-store, and generation primitives

This notebook is a reference walkthrough, not an additional assignment. Its purpose is to make the responsibilities hidden by LangChain, Qdrant, and provider SDKs visible.

---

## Submitting Your Homework

### Main Assignment

Follow these steps to prepare and submit your homework:

1. Pull the latest updates from upstream into the main branch of your AIE9 repo:

```bash
git checkout main
git pull upstream main
git push origin main
```

2. Start Cursor from the `01_Dense_Vector_Retrieval` folder.
3. Complete the notebook.
4. Answer the questions in this `README.md`.
5. Add, commit, and push your modified work to your origin repository.

When submitting your homework, provide the GitHub URL to your AIE9 repo.
