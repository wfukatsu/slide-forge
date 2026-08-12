*[日本語](research-2026-08.ja.md)*

# Scalar Product & Company Research Summary (conducted 2026-08-01)

**Freshness warning**: This file reflects public information as of 2026-08-01. Versions,
news, and case studies go stale, so **if more than 3 months have passed since the
research date, re-research before using this file**
(dispatch research agents in parallel against scalar-labs.com / developers.scalar-labs.com).

## Company (sources: scalar-labs.com/ja/company, STARTUP DB)

- Scalar, Inc. (株式会社Scalar). Founded December 2017. Tokyo (Kagurazaka), Sapporo, San Francisco (US Scalar Labs)
- Representatives: Wataru Fukatsu (Founder/Representative Director & CEO), Hiroyuki Yamada (Founder/Representative Director & CTO) *per the boilerplate official slides
- US entity CEO: Joe McCunney. Approx. 50 employees (July 2026, STARTUP DB)
- Vision: "Creating the future of data management" / Tagline: "Absolute data reliability"
- Values: Quality Obsessed / Customer Focus / Frontier Spirit
- History: Oct 2018 ScalarDB OSS released → 2019 FIBC Grand Prix → Nov 2022 Series A JPY 1.5B →
  2022-23 VLDB accepted two years running → Dec 2023 strengthened executive officer structure
- **Capital amount unconfirmed from primary sources → do not state it**

## Recent topics (2025-2026)

- May 2026 ScalarDB 3.18 (enhanced ABAC, OIDC, Spanner support, extended one-phase commit)
- Mar 2026 ScalarDL 3.13 (namespace management, Java 21) *news reported this as April, but the release notes are dated 3/25
- Jan 2026 Kong partnership / Dec 2025 ScalarDB 3.17 / Oct 2025 MCP Server & Zenrin collaboration
- Jun 2025 strengthened NSW mainframe modernization / Apr 2025 corporate PPA proof of concept

## ScalarDB (latest 3.18.0, 2026-05-01)

- Universal HTAP engine. Core (OSS/Apache 2.0) + Cluster (commercial/K8s) + Analytics (commercial/Spark)
- DB-agnostic ACID via Consensus Commit. Supports: RDBMS (MySQL/PostgreSQL/Oracle/SQL Server/Db2, etc.),
  NewSQL (Aurora/AlloyDB/Spanner/TiDB/YugabyteDB), NoSQL (DynamoDB/Cassandra/Cosmos DB)
- 15 features: ACID / multi-storage / 2PC (microservices) / Cluster / SQL / GraphQL / authentication & authorization / encryption /
  ABAC / vector search / non-transactional / remote replication / Analytics / MCP Server / --import
- Example pricing (Marketplace, Pod=2vCPU/4GB): Standard $1.40/h, Premium $2.79/h (AWS)

## ScalarDL (latest 3.13.0, 2026-03-25)

- Byzantine fault detection middleware. 2 administrative domains (Ledger+Auditor), tens of thousands of TPS, ACID
- 9 features: BFT detection / Ledger / Auditor / Contract / Function / TableStore (3.12) / HashStore (3.12) /
  Namespace (3.13) / Asset Proof
- Editions: Ledger=Community, Ledger (BYOL)/Auditor (BYOL)=Enterprise

## Use cases and published case studies

- Toyota Motor Corporation PCE (ScalarDL/Azure, IP evidence preservation) *official slides exist in the boilerplate
- Major broadcaster content data management (ScalarDB) *official slides exist in the boilerplate
- ENS 30-minute electricity volume data (ScalarDB): **statutory reporting work reduced to 1/5 — the only published quantitative result**
- J-POWER environmental value platform (ScalarDL, from Jan 2025) / NSW COBOL migration (ScalarDB) / LayerX Ai Workforce (ScalarDB, Oct 2024)
- Toyota Financial Services proof of concept (Mar 2020) / NTT Digital & docomo Web3 partnership (Jul 2023, details unknown)
- Tsuneishi Shipbuilding core system modernization (ScalarDB + Kong Konnect, announced 2026-06-10, researched 2026-08-02):
  Modernized a monolith that had run for 15+ years using AI-driven development. Current-state analysis and redesign took 2 days, MVP took roughly 3 months,
  2 Scalar IT staff were embedded on-site, resulting in a 9-microservice structure organized by business domain.
  Sources: prtimes.jp/main/html/rd/p/000000071.000037795.html /
  atmarkit.itmedia.co.jp/ait/articles/2606/29/news054.html /
  jp.konghq.com/news/kong-tsuneishi-ai-core-system-modernization
- Patterns: DB = silo consolidation, microservices consistency, legacy migration, multi-cloud, generative AI infrastructure, high-volume data /
  DL = tamper detection, audit trails, traceability, blockchain alternative

## Known pitfalls (when turning this into slides)

1. **Inconsistent edition assignment for the SQL interface** (features page: Premium / pricing page: Standard).
   Follow the features table and add a "needs confirmation" note
2. **Note preview status explicitly**: ABAC (private preview, Japan only) / remote replication (private preview) /
   vector search (public preview)
3. **The phrase "zero schema changes" does not appear in the docs** → the official term is Schema Loader `--import` (importing existing tables)
4. **ScalarDL's "SQL support" officially takes the form of TableStore** (not a standalone feature name)
5. There is no dedicated page for case studies (only news/blog posts). ENS's 1/5 is the only quantitative result
6. Authentication/authorization is also inconsistent between the features table (Standard and above) and individual pages (Premium tag) → follow the features table and add a note
