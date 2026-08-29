# ORCA — RAG Architecture

**Project Name:** ORCA
**Document:** RAG Architecture
**Document ID:** ORCA-RAG-10
**Version:** 1.0
**Status:** FROZEN BASELINE
**Scope:** Document Ingestion, Chunking, Embeddings, Vector Storage, Retrieval, Reranking, Evidence and Agent Integration

---

# 1. Purpose

The ORCA RAG subsystem provides reliable retrieval of relevant knowledge from unstructured and semi-structured documents.

The RAG subsystem supports:

- Marine scientific knowledge
- Fisheries knowledge
- Oceanographic documentation
- Marine safety guidelines
- Government publications
- Marine advisories
- Regulations
- Operational guidelines
- Technical documentation
- Scientific papers
- Reference material

RAG provides contextual knowledge and evidence to the agentic system.

---

# 2. Core Principle

ORCA does NOT use RAG for everything.

The architecture separates:

```text
STRUCTURED INTELLIGENCE
        +
GEOSPATIAL INTELLIGENCE
        +
REAL-TIME DATA
        +
RAG KNOWLEDGE
````

Example:

```text
"Where is the nearest PFZ?"

        ↓

PostGIS / PFZ Data

NOT:

        ↓

Vector Search
```

Whereas:

```text
"What does this marine safety regulation mean?"

        ↓

RAG
```

---

# 3. RAG Architecture

```text
                    DOCUMENT SOURCES
                          │
             ┌────────────┼────────────┐
             │            │            │
            PDF         HTML        Documents
             │            │            │
             └────────────┼────────────┘
                          ▼
                   DOCUMENT INGESTION
                          │
                          ▼
                    OBJECT STORAGE
                       (MinIO)
                          │
                          ▼
                    TEXT EXTRACTION
                          │
                          ▼
                       CLEANING
                          │
                          ▼
                      CHUNKING
                          │
                          ▼
                    METADATA ENRICHMENT
                          │
                          ▼
                      EMBEDDINGS
                          │
                          ▼
                       QDRANT
                          │
                          ▼
                      RETRIEVAL
                          │
                          ▼
                       RERANKING
                          │
                          ▼
                       EVIDENCE
                          │
                          ▼
                     RAG AGENT
                          │
                          ▼
                   ORCHESTRATOR
                          │
                          ▼
                        LLM
                          │
                          ▼
                    USER RESPONSE
```

---

# 4. RAG Components

The ORCA RAG subsystem contains:

```text
1. Document Sources
2. Document Ingestion
3. Object Storage
4. Text Extraction
5. Document Cleaning
6. Chunking
7. Metadata Extraction
8. Embedding Generation
9. Vector Storage
10. Retrieval
11. Filtering
12. Reranking
13. Context Assembly
14. Evidence Tracking
15. LLM Generation
```

---

# 5. Document Sources

Potential source types:

```text
PDF
HTML
DOCX
TXT
Markdown
CSV documentation
Government publications
Scientific papers
Marine advisories
Safety manuals
Regulatory documents
Technical documentation
```

---

# 6. Document Trust Hierarchy

Not every document has equal authority.

ORCA should classify sources.

```text
LEVEL 1
Official Government / Regulatory Source

LEVEL 2
Official Scientific / Institutional Source

LEVEL 3
Peer-reviewed Scientific Source

LEVEL 4
Trusted Technical Documentation

LEVEL 5
Secondary Reference

LEVEL 6
Unknown / Unverified
```

The exact trust policy can be refined during implementation.

---

# 7. Document Metadata

Every document should have metadata.

Minimum fields:

```text
document_id
title
source
provider
document_type
publication_date
language
version
url/reference
ingestion_timestamp
```

Additional metadata:

```text
authority
region
topic
valid_from
valid_until
license
```

---

# 8. Document Storage

Original documents should be stored in MinIO.

Example:

```text
documents/
├── scientific/
├── fisheries/
├── safety/
├── regulations/
├── advisories/
└── technical/
```

The vector database should not be treated as the original document store.

---

# 9. Why MinIO + Qdrant?

These components have different responsibilities.

```text
MinIO
  ↓
Original / processed files

Qdrant
  ↓
Vector representations for retrieval
```

Therefore:

```text
MinIO = Object Storage

Qdrant = Vector Search
```

---

# 10. Text Extraction

The ingestion layer extracts textual content from supported documents.

```text
Document
   ↓
Parser
   ↓
Text
```

For PDFs:

```text
PDF
 ↓
Text Extraction
 ↓
Page-aware Text
```

Page information should be preserved where possible.

---

# 11. Page-Level Metadata

For documents such as PDFs, chunks should retain:

```text
document_id
page_number
section
chunk_id
```

This allows ORCA to identify where retrieved evidence came from.

---

# 12. Document Cleaning

Cleaning may include:

```text
Remove repeated headers
Remove repeated footers
Normalize whitespace
Remove unnecessary formatting
Repair broken text
Normalize encoding
```

Cleaning must not alter the meaning of the source.

---

# 13. Chunking

Documents are divided into smaller chunks.

```text
DOCUMENT
   ↓
SECTIONS
   ↓
PARAGRAPHS
   ↓
CHUNKS
```

Chunking should preserve semantic boundaries wherever practical.

---

# 14. Chunk Size

Chunk size should be configurable.

The system should not hard-code one universal size.

Initial implementation can use:

```text
~500–1000 tokens
```

with configurable overlap.

The final value should be tuned using retrieval evaluation.

---

# 15. Chunk Overlap

Adjacent chunks may overlap.

Example:

```text
Chunk A
████████████████

       overlap

          ████████████████
          Chunk B
```

Overlap helps preserve context across chunk boundaries.

---

# 16. Semantic Chunking

Where practical, ORCA should prefer semantic boundaries.

Priority:

```text
Section
   ↓
Subsection
   ↓
Paragraph
   ↓
Token-based fallback
```

This is preferable to blindly splitting every N characters.

---

# 17. Chunk Metadata

Each chunk should contain:

```text
chunk_id
document_id
text
page
section
source
provider
document_type
publication_date
language
region
topic
trust_level
```

---

# 18. Embeddings

Each chunk is converted into a vector representation.

```text
Text Chunk
    ↓
Embedding Model
    ↓
Vector
```

The embedding model should be selected based on:

* Semantic retrieval quality
* Multilingual support
* Computational requirements
* Embedding dimensions
* Deployment constraints

---

# 19. Multilingual Embeddings

ORCA must support multilingual interaction.

The embedding layer should therefore use a model capable of handling relevant Indian languages where practical.

The architecture should not assume English-only embeddings.

---

# 20. Vector Database

ORCA uses:

```text
Qdrant
```

for vector retrieval.

Qdrant stores:

```text
Vector
+
Chunk ID
+
Metadata
```

---

# 21. Qdrant Collection

A primary ORCA knowledge collection can conceptually be:

```text
orca_knowledge
```

Additional collections can be introduced when justified.

---

# 22. Vector Payload

A vector record should contain payload metadata similar to:

```json
{
  "document_id": "...",
  "chunk_id": "...",
  "title": "...",
  "source": "...",
  "page": 12,
  "section": "...",
  "language": "en",
  "topic": "marine_safety",
  "trust_level": "official"
}
```

---

# 23. Retrieval

When a user asks a knowledge-based question:

```text
User Query
    ↓
Query Understanding
    ↓
Query Embedding
    ↓
Qdrant Search
    ↓
Candidate Chunks
```

---

# 24. Metadata Filtering

Vector similarity alone is not always sufficient.

ORCA should support filtering by:

```text
language
region
topic
document type
source
date
trust level
```

Example:

```text
topic = marine_safety
region = India
language = English
```

---

# 25. Top-K Retrieval

The retriever should return a configurable number of candidates.

Example:

```text
Query
 ↓
Retrieve Top-K
 ↓
Candidate Evidence
```

The value of K should be configurable and evaluated rather than permanently hard-coded.

---

# 26. Reranking

Initial vector search provides candidate results.

A reranker can then improve relevance.

```text
Query
  ↓
Vector Search
  ↓
Top-K Candidates
  ↓
Reranker
  ↓
Top-N Evidence
```

---

# 27. Why Reranking?

Two chunks may both be semantically related but only one may directly answer the question.

Reranking allows ORCA to consider:

```text
Query relevance
Semantic similarity
Metadata
Source quality
```

before constructing the final context.

---

# 28. Hybrid Retrieval

ORCA should support hybrid retrieval where useful.

Conceptually:

```text
               USER QUERY
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   Semantic Search       Keyword Search
          │                   │
          └─────────┬─────────┘
                    ▼
              Result Fusion
                    │
                    ▼
                Reranking
                    │
                    ▼
                 Evidence
```

This helps with:

* Technical terms
* Regulation numbers
* Dataset names
* Exact phrases
* Scientific terminology

---

# 29. Query Expansion

The RAG agent may transform the user's question into search-oriented queries.

Example:

```text
User:
"Can I fish in this protected area?"

Potential retrieval concepts:

"marine protected area fishing restrictions"
"fishing prohibited protected waters"
"Indian marine protected area regulations"
```

The expansion must preserve user intent.

---

# 30. Query Decomposition

Complex knowledge questions may be split.

Example:

```text
"What restrictions apply to fishing near this protected area?"
```

Could require:

```text
Protected area rules
+
Fishing restrictions
+
Regional regulation
```

The RAG agent can retrieve evidence for each component.

---

# 31. RAG Agent

The RAG Agent is responsible for:

```text
Understanding knowledge requirements
Generating retrieval queries
Selecting filters
Calling retrieval tools
Evaluating retrieved evidence
Returning evidence to orchestrator
```

It should not invent missing facts.

---

# 32. RAG Agent Output

Conceptually:

```json
{
  "answerable": true,
  "evidence": [
    {
      "document_id": "...",
      "chunk_id": "...",
      "title": "...",
      "page": 12,
      "relevance": 0.91,
      "trust_level": "official"
    }
  ]
}
```

The actual schema will be defined in the API specification.

---

# 33. Context Assembly

Retrieved chunks are converted into structured context.

```text
Retrieved Evidence
        ↓
Deduplication
        ↓
Relevance Ordering
        ↓
Source Quality
        ↓
Context Window
```

Only useful evidence should be sent to the generation model.

---

# 34. Context Budget

The system should control context size.

Too much retrieved text can:

```text
Increase latency
Increase cost
Reduce relevance
Overload the model
```

Therefore ORCA should retrieve and rerank before final context construction.

---

# 35. Evidence First

The LLM should receive:

```text
QUESTION
+
RETRIEVED EVIDENCE
+
STRUCTURED DATA
+
AGENT RESULTS
```

rather than being asked to answer from memory.

---

# 36. RAG + Structured Data

This is one of ORCA's most important design principles.

Example:

```text
Question:
"Is it safe to fish tomorrow near this area?"

RAG:
Marine safety guidelines
+
Official advisories

Structured:
Weather
+
Wave conditions
+
Wind
+
Lightning
+
Cyclone

Geospatial:
Protected areas
+
Boundaries
```

All three can contribute to the final response.

---

# 37. RAG + Geospatial Intelligence

Example:

```text
Question:
"Can I fish in this region?"

Geospatial Agent:
    Is region inside restricted area?

RAG Agent:
    What regulations apply?

Orchestrator:
    Combine both
```

---

# 38. RAG + Marine Intelligence

Example:

```text
PFZ
+
SST
+
Chlorophyll
+
Marine Scientific Knowledge
```

The structured system determines the observations.

RAG provides scientific context explaining what those observations may indicate.

---

# 39. RAG + Risk Assessment

RAG can provide:

```text
Safety guidelines
Advisory interpretation
Regulatory requirements
Hazard definitions
```

The Risk Engine provides:

```text
Numerical risk assessment
```

The LLM explains the combination.

---

# 40. RAG + Routing

RAG may provide:

```text
Navigation guidance
Safety guidelines
Regulatory restrictions
```

Routing services provide:

```text
Candidate routes
Distances
Hazard intersections
Geofences
Risk scores
```

---

# 41. Source Citations

Final answers should identify supporting sources where applicable.

Conceptually:

```text
Recommendation
      ↓
Evidence
      ↓
Source
      ↓
Document
      ↓
Page / Section
```

For PDF documents:

```text
Source:
Marine Safety Guidelines
Page:
12
```

---

# 42. Citation Requirements

RAG-generated claims should be traceable to retrieved evidence.

The generation layer should avoid presenting unsupported factual claims as if they came from the source.

---

# 43. Citation Metadata

Evidence should retain:

```text
document_id
chunk_id
source
title
page
section
publication_date
retrieval_score
trust_level
```

---

# 44. Evidence Ranking

A conceptual ranking model can consider:

```text
Semantic Relevance
+
Keyword Relevance
+
Source Trust
+
Recency
+
Metadata Match
```

The exact formula belongs to the retrieval implementation.

---

# 45. Conflicting Sources

Different documents may disagree.

ORCA should not silently merge contradictory information.

Instead:

```text
Source A:
Rule X

Source B:
Rule Y

       ↓

Conflict Detection

       ↓

Present discrepancy
```

The system should prioritize authoritative and current sources according to the trust policy.

---

# 46. Outdated Documents

Documents with validity periods should be checked.

Example:

```text
Document
   ↓
Valid Until
   ↓
Expired?
```

If expired:

```text
Do not treat as current regulation
```

unless the user explicitly asks for historical information.

---

# 47. Knowledge Freshness

Different document types require different refresh policies.

```text
Regulations
→ monitor updates

Advisories
→ frequently updated

Scientific papers
→ relatively stable

Technical documentation
→ version-dependent
```

---

# 48. Document Versioning

When a source publishes a new version:

```text
Old Version
     ↓
New Version
```

ORCA should retain version information.

For current queries, the latest valid version should normally be preferred.

---

# 49. RAG Failure Modes

Potential failures:

```text
No relevant documents
Poor retrieval
Incorrect chunking
Outdated source
Conflicting sources
Low-quality source
Embedding mismatch
Language mismatch
```

---

# 50. No-Answer Policy

If the RAG system cannot find reliable evidence:

```text
No reliable evidence found
```

The LLM must not fabricate a source-backed answer.

---

# 51. Retrieval Confidence

The system can maintain:

```text
retrieval_score
source_trust
evidence_count
```

These can contribute to an evidence-quality indicator.

---

# 52. RAG Evaluation

RAG quality should be evaluated separately from LLM quality.

Metrics may include:

```text
Recall@K
Precision@K
MRR
NDCG
Answer groundedness
Citation correctness
```

---

# 53. Retrieval Test Set

A dedicated evaluation dataset should contain questions such as:

```text
Marine safety questions
Fishing regulations
PFZ interpretation
Oceanographic concepts
Weather safety
Protected-area rules
Navigation guidance
```

Each question should have expected supporting documents.

---

# 54. RAG Observability

The system should log:

```text
Query
Retrieval time
Retrieved document IDs
Scores
Reranking results
Final evidence
LLM response
```

Avoid storing sensitive user information unnecessarily.

---

# 55. RAG Performance

Optimization options include:

```text
Embedding caching
Query caching
Vector indexing
Metadata filtering
Result caching
Batch embedding
Asynchronous ingestion
```

---

# 56. RAG Caching

Frequently repeated knowledge queries may use Redis.

```text
Query
 ↓
Redis
 ↓
Cached?
 ┌──┴──┐
Yes   No
 │     │
 ▼     ▼
Return Qdrant
       ↓
     Redis
```

Cache expiration should reflect document freshness.

---

# 57. RAG Security

The system must:

```text
Validate uploaded documents
Limit file sizes
Prevent malicious content where applicable
Protect credentials
Restrict administrative operations
Avoid executing document content
```

---

# 58. Prompt Injection Protection

Documents may contain instructions that attempt to manipulate the LLM.

Retrieved text must be treated as:

```text
DATA / EVIDENCE
```

not as executable instructions.

The generation prompt should explicitly separate:

```text
SYSTEM INSTRUCTIONS
USER REQUEST
RETRIEVED EVIDENCE
```

---

# 59. RAG Agent Boundary

The RAG Agent should not:

```text
Calculate route distances
Modify geofences
Invent weather values
Generate PFZ coordinates
Override deterministic safety rules
```

It should retrieve and interpret knowledge.

---

# 60. LLM Boundary

The LLM should not become the source of truth for:

```text
Coordinates
Weather measurements
Wave heights
SST values
Chlorophyll values
Distances
Geofence intersections
Risk calculations
```

Those come from structured tools and analytical services.

---

# 61. Complete RAG Flow

```text
                         USER QUERY
                              │
                              ▼
                         ORCHESTRATOR
                              │
                              ▼
                       KNOWLEDGE REQUIRED?
                              │
                              ▼
                         RAG AGENT
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
              Query Expansion       Metadata
                    │                Filtering
                    └─────────┬─────────┘
                              ▼
                       QDRANT RETRIEVAL
                              │
                              ▼
                          TOP-K
                              │
                              ▼
                         RERANKING
                              │
                              ▼
                    EVIDENCE SELECTION
                              │
                              ▼
                     CONTEXT ASSEMBLY
                              │
                              ▼
                           LLM
                              │
                              ▼
                    GROUNDED RESPONSE
                              │
                              ▼
                          CITATIONS
```

---

# 62. Complete Hybrid ORCA Retrieval

ORCA can perform multiple retrieval operations simultaneously.

```text
                         USER QUERY
                              │
                         ORCHESTRATOR
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
       ▼                      ▼                      ▼
   PostgreSQL              PostGIS               Qdrant
 Structured Data        Spatial Data          Knowledge
       │                      │                      │
       └──────────────────────┼──────────────────────┘
                              │
                              ▼
                     CROSS-DATASET ANALYSIS
                              │
                              ▼
                           AGENTS
                              │
                              ▼
                         RISK / ROUTE
                              │
                              ▼
                          EVIDENCE
                              │
                              ▼
                            LLM
                              │
                              ▼
                           USER
```

---

# 63. Example — Regulation Question

User:

> "Can fishing be carried out inside this protected area?"

Flow:

```text
User
 ↓
Orchestrator
 ↓
Geospatial Agent
 ↓
Determine Protected Area
 ↓
RAG Agent
 ↓
Retrieve Applicable Regulation
 ↓
Retrieve Current Source
 ↓
Evidence Validation
 ↓
Orchestrator
 ↓
Answer
```

---

# 64. Example — Scientific Question

User:

> "Why is chlorophyll important for identifying productive fishing areas?"

Flow:

```text
User
 ↓
RAG Agent
 ↓
Scientific Knowledge Retrieval
 ↓
Qdrant
 ↓
Reranking
 ↓
Evidence
 ↓
LLM
 ↓
Explanation
```

---

# 65. Example — Hybrid Question

User:

> "Why is this PFZ considered favourable?"

Flow:

```text
PFZ Data
   +
SST
   +
Chlorophyll
   +
Scientific Knowledge
        ↓
Cross-Dataset Analysis
        ↓
RAG Evidence
        ↓
Ocean Analytics Agent
        ↓
Explanation
```

---

# 66. Example — Safety Question

User:

> "Is it safe to venture into the sea tomorrow?"

Structured sources:

```text
Weather
Wind
Waves
Lightning
Cyclone
Tides
```

Knowledge sources:

```text
Marine safety guidance
Official advisories
```

Final:

```text
Structured Risk Assessment
+
Official Guidance
+
Evidence
+
Explanation
```

---

# 67. RAG Technology Stack

The RAG subsystem uses:

```text
Object Storage:
MinIO

Vector Database:
Qdrant

Structured Metadata:
PostgreSQL

Spatial Metadata:
PostGIS

Cache:
Redis

Document Processing:
Python

Embedding Model:
Multilingual-capable embedding model

LLM:
Configured ORCA LLM provider

API:
FastAPI
```

---

# 68. RAG Does Not Replace Databases

```text
PostgreSQL
→ structured information

PostGIS
→ spatial information

MinIO
→ large files

Qdrant
→ semantic knowledge

Redis
→ cache
```

All five serve different purposes.

---

# 69. RAG Does Not Replace Agents

The RAG system is one capability inside ORCA.

```text
                 ORCA
                   │
        ┌──────────┼──────────┐
        │          │          │
       RAG       Marine      Weather
        │          │          │
        └──────────┼──────────┘
                   │
                 Agents
```

---

# 70. RAG Does Not Replace Deterministic Analytics

Example:

```text
"What is 12 km from this PFZ?"

→ PostGIS

"Which route has lower calculated risk?"

→ Risk / Routing Engine

"What does this regulation mean?"

→ RAG
```

---

# 71. Final RAG Architecture

```text
                         DOCUMENTS
                            │
                            ▼
                       MINIO STORAGE
                            │
                            ▼
                    TEXT EXTRACTION
                            │
                            ▼
                         CLEANING
                            │
                            ▼
                        CHUNKING
                            │
                            ▼
                       METADATA
                            │
                            ▼
                      EMBEDDINGS
                            │
                            ▼
                         QDRANT
                            │
                            ▼
                       RETRIEVAL
                            │
                     ┌──────┴──────┐
                     │             │
               Semantic        Keyword
                Search          Search
                     │             │
                     └──────┬──────┘
                            ▼
                         FUSION
                            │
                            ▼
                        RERANKING
                            │
                            ▼
                     EVIDENCE LAYER
                            │
                            ▼
                       RAG AGENT
                            │
                            ▼
                      ORCHESTRATOR
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
      PostgreSQL          PostGIS          External APIs
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                            ▼
                    CROSS-DATASET ANALYSIS
                            │
                            ▼
                           LLM
                            │
                            ▼
                     GROUNDED RESPONSE
                            │
                            ▼
                         EVIDENCE
```

---

# 72. Frozen RAG Principles

ORCA's RAG architecture officially follows these principles:

1. RAG is only one component of ORCA.
2. Numerical marine data is not stored as vectors for primary retrieval.
3. Spatial queries use PostGIS.
4. Structured observations use PostgreSQL.
5. Large source files use MinIO.
6. Semantic knowledge uses Qdrant.
7. Redis is used for caching and temporary state.
8. Retrieved documents are evidence, not executable instructions.
9. Source metadata must be preserved.
10. Page/section information should be preserved where possible.
11. Retrieval should support metadata filtering.
12. Hybrid retrieval should be supported.
13. Reranking should be supported.
14. Source trust and freshness matter.
15. Conflicting sources must not be silently merged.
16. Unsupported answers should not be fabricated.
17. Final claims should be traceable to evidence where applicable.
18. RAG and structured intelligence must work together.
19. The LLM explains evidence rather than inventing observations.
20. The RAG architecture must remain modular and replaceable.
