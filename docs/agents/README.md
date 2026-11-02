# Agency Agents — Claude Code Integration

This workspace includes **232 Claude Code agents** from [The Agency](https://github.com/msitarzewski/agency-agents),
installed under `.claude/agents/`. They activate automatically in every Claude Code session.

## How Agents Work in Claude Code

Claude Code loads all `.md` files in `.claude/agents/` as subagents. You invoke them
by name in your session, or Claude selects the appropriate agent automatically based on context.

### Activating an Agent Explicitly

```
Use the Frontend Developer agent to build a React component for the user dashboard.
```

```
Activate the Code Reviewer and review the changes in src/auth.ts.
```

```
Use the Security Penetration Tester to audit this API for vulnerabilities.
```

### Letting Claude Choose

Claude Code reads agent descriptions and picks the best fit automatically:

```
Review this code for security issues.          → Security AppSec Engineer
Write unit tests for the payment module.       → Testing API Tester
Design a new onboarding flow.                  → Design UX Researcher + UX Architect
Optimize this database query.                  → Engineering Database Optimizer
```

### Chaining Agents (Multi-Agent Workflows)

Agents can hand off work to each other:

```
Use the UX Researcher to gather requirements, then hand off to the UI Designer
to create wireframes, then have the Frontend Developer implement it.
```

See `agency-agents/strategy/` and `agency-agents/examples/` for full workflow playbooks.

---

## Agent Roster by Division

### Academic (5 agents)
| Slug | Name | Description |
|------|------|-------------|
| `academic-anthropologist` | Anthropologist | Cultural systems, rituals, kinship, belief systems, ethnographic methods |
| `academic-geographer` | Geographer | Physical and human geography, climate systems, cartography, spatial analysis |
| `academic-historian` | Historian | Historical analysis, periodization, material culture, historiography |
| `academic-narratologist` | Narratologist | Narrative theory, story structure, character arcs, literary analysis |
| `academic-psychologist` | Psychologist | Human behavior, personality theory, motivation, cognitive patterns |

### Design (9 agents)
| Slug | Name | Description |
|------|------|-------------|
| `design-brand-guardian` | Brand Guardian | Brand identity, style guides, consistency across all touchpoints |
| `design-image-prompt-engineer` | Image Prompt Engineer | Crafting detailed prompts for AI image generation tools |
| `design-inclusive-visuals-specialist` | Inclusive Visuals Specialist | Representation, defeating AI biases, culturally accurate visuals |
| `design-persona-walkthrough` | Persona Walkthrough Specialist | Cognitive walkthroughs from defined persona perspectives |
| `design-ui-designer` | UI Designer | Visual design systems, component libraries, interaction design |
| `design-ux-architect` | UX Architect | Technical architecture and UX foundations for developers |
| `design-ux-researcher` | UX Researcher | User behavior analysis, usability testing, research synthesis |
| `design-visual-storyteller` | Visual Storyteller | Visual narrative, data visualization, presentation design |
| `design-whimsy-injector` | Whimsy Injector | Adding personality, delight, and playful elements to interfaces |

### Engineering (33 agents)
| Slug | Name | Description |
|------|------|-------------|
| `engineering-ai-data-remediation-engineer` | AI Data Remediation Engineer | Data quality, pipeline repair, AI training data cleanup |
| `engineering-ai-engineer` | AI Engineer | LLM integration, RAG, embeddings, AI system design |
| `engineering-autonomous-optimization-architect` | Autonomous Optimization Architect | Self-optimizing systems, adaptive algorithms |
| `engineering-backend-architect` | Backend Architect | API design, microservices, system architecture |
| `engineering-cms-developer` | CMS Developer | Content management systems, headless CMS, publishing workflows |
| `engineering-code-reviewer` | Code Reviewer | Constructive code review for correctness, maintainability, security |
| `engineering-codebase-onboarding-engineer` | Codebase Onboarding Engineer | Orienting developers to new codebases |
| `engineering-data-engineer` | Data Engineer | Data pipelines, ETL, warehousing, streaming |
| `engineering-database-optimizer` | Database Optimizer | Query optimization, indexing, schema design |
| `engineering-devops-automator` | DevOps Automator | CI/CD, infrastructure automation, deployment pipelines |
| `engineering-drupal-shopping-cart` | Drupal Shopping Cart | Drupal e-commerce, Commerce module, cart UX |
| `engineering-email-intelligence-engineer` | Email Intelligence Engineer | Email parsing, classification, automation |
| `engineering-embedded-firmware-engineer` | Embedded Firmware Engineer | Low-level firmware, RTOS, embedded C/C++ |
| `engineering-feishu-integration-developer` | Feishu Integration Developer | Feishu/Lark platform integrations and bots |
| `engineering-filament-optimization-specialist` | Filament Optimization Specialist | Laravel Filament admin panels, performance |
| `engineering-frontend-developer` | Frontend Developer | React/Vue/Angular, performance, accessibility, responsive design |
| `engineering-git-workflow-master` | Git Workflow Master | Git branching, rebasing, merge strategies, history hygiene |
| `engineering-incident-response-commander` | Incident Response Commander | Production incidents, war-room coordination, postmortems |
| `engineering-it-service-manager` | IT Service Manager | ITSM, ticketing, SLAs, change management |
| `engineering-minimal-change-engineer` | Minimal Change Engineer | Surgical fixes with minimal blast radius |
| `engineering-mobile-app-builder` | Mobile App Builder | React Native, Flutter, native iOS/Android |
| `engineering-multi-agent-systems-architect` | Multi-Agent Systems Architect | Designing and orchestrating multi-agent AI workflows |
| `engineering-orgscript-engineer` | OrgScript Engineer | Org-mode, Emacs scripting, literate programming |
| `engineering-prompt-engineer` | Prompt Engineer | LLM prompt design, few-shot examples, chain-of-thought |
| `engineering-rapid-prototyper` | Rapid Prototyper | Fast proof-of-concept, throwaway code, validation builds |
| `engineering-senior-developer` | Senior Developer | Full-stack, Laravel/Livewire, premium web experiences |
| `engineering-software-architect` | Software Architect | System design, architecture patterns, tech decisions |
| `engineering-solidity-smart-contract-engineer` | Solidity Smart Contract Engineer | EVM, smart contracts, DeFi, auditing |
| `engineering-sre` | SRE | Reliability, SLOs, observability, chaos engineering |
| `engineering-technical-writer` | Technical Writer | API docs, runbooks, READMEs, developer guides |
| `engineering-voice-ai-integration-engineer` | Voice AI Integration Engineer | Speech recognition, TTS, voice interfaces |
| `engineering-wechat-mini-program-developer` | WeChat Mini Program Developer | WeChat Mini Program platform and APIs |
| `engineering-wordpress-shopping-cart` | WordPress Shopping Cart | WooCommerce, WordPress e-commerce, payment gateways |

### Finance (5 agents)
| Slug | Name | Description |
|------|------|-------------|
| `finance-bookkeeper-controller` | Bookkeeper / Controller | Bookkeeping, accounts, financial close process |
| `finance-financial-analyst` | Financial Analyst | Financial modeling, valuation, investment analysis |
| `finance-fpa-analyst` | FP&A Analyst | Financial planning, budgeting, variance analysis |
| `finance-investment-researcher` | Investment Researcher | Market research, due diligence, sector analysis |
| `finance-tax-strategist` | Tax Strategist | Tax planning, compliance, optimization strategies |

### Game Development (20 agents)
| Slug | Name | Description |
|------|------|-------------|
| `blender-addon-engineer` | Blender Addon Engineer | Blender Python API, custom tools, pipeline automation |
| `game-audio-engineer` | Game Audio Engineer | Sound design, FMOD/Wwise, adaptive audio |
| `game-designer` | Game Designer | Game mechanics, systems design, balancing |
| `godot-gameplay-scripter` | Godot Gameplay Scripter | GDScript, Godot 4 gameplay systems |
| `godot-multiplayer-engineer` | Godot Multiplayer Engineer | Godot networking, ENet, multiplayer sync |
| `godot-shader-developer` | Godot Shader Developer | GLSL shaders in Godot, visual effects |
| `level-designer` | Level Designer | Level flow, environmental storytelling, pacing |
| `narrative-designer` | Narrative Designer | Interactive narrative, branching dialogue, world-building |
| `roblox-avatar-creator` | Roblox Avatar Creator | Roblox avatar items, layered clothing |
| `roblox-experience-designer` | Roblox Experience Designer | Roblox game design, Studio workflow |
| `roblox-systems-scripter` | Roblox Systems Scripter | Luau scripting, Roblox game systems |
| `technical-artist` | Technical Artist | Shader development, art pipeline, tool scripting |
| `unity-architect` | Unity Architect | Unity project architecture, patterns, performance |
| `unity-editor-tool-developer` | Unity Editor Tool Developer | Custom Unity editor scripts and tools |
| `unity-multiplayer-engineer` | Unity Multiplayer Engineer | Netcode for GameObjects, Mirror, lobby systems |
| `unity-shader-graph-artist` | Unity Shader Graph Artist | Unity Shader Graph, URP/HDRP visual effects |
| `unreal-multiplayer-architect` | Unreal Multiplayer Architect | Unreal Engine replication, dedicated servers |
| `unreal-systems-engineer` | Unreal Systems Engineer | Unreal gameplay systems, C++/Blueprints |
| `unreal-technical-artist` | Unreal Technical Artist | Niagara, materials, Unreal art pipeline |
| `unreal-world-builder` | Unreal World Builder | World Partition, landscapes, environment design |

### GIS (13 agents)
| Slug | Name | Description |
|------|------|-------------|
| `gis-3d-scene-developer` | GIS 3D Scene Developer | 3D geospatial visualization, CesiumJS, scene layers |
| `gis-analyst` | GIS Analyst | Spatial analysis, GIS workflows, data interpretation |
| `gis-bim-specialist` | GIS BIM Specialist | BIM/GIS integration, IFC, digital twins |
| `gis-cartography-designer` | Cartography Designer | Map design, symbology, visual communication |
| `gis-drone-reality-mapping` | Drone Reality Mapping | UAV data processing, photogrammetry, point clouds |
| `gis-geoai-ml-engineer` | GeoAI / ML Engineer | Geospatial ML, satellite image analysis, spatial AI |
| `gis-geoprocessing-specialist` | Geoprocessing Specialist | Automation scripts, spatial ETL, model builder |
| `gis-qa-engineer` | GIS QA Engineer | Geospatial data quality, validation, accuracy |
| `gis-solution-engineer` | GIS Solution Engineer | Esri/ArcGIS implementation, client solutions |
| `gis-spatial-data-engineer` | Spatial Data Engineer | Geospatial databases, PostGIS, spatial pipelines |
| `gis-spatial-data-scientist` | Spatial Data Scientist | Statistical spatial analysis, predictive modeling |
| `gis-technical-consultant` | GIS Technical Consultant | GIS strategy, architecture, stakeholder guidance |
| `gis-web-gis-developer` | Web GIS Developer | Leaflet, MapboxGL, ArcGIS JS API, web mapping |

### Marketing (36 agents)
| Slug | Name | Description |
|------|------|-------------|
| `marketing-aeo-foundations` | AEO Foundations | Answer Engine Optimization fundamentals |
| `marketing-agentic-search-optimizer` | Agentic Search Optimizer | Optimizing for AI-driven search and agents |
| `marketing-ai-citation-strategist` | AI Citation Strategist | Getting cited by AI models and LLMs |
| `marketing-app-store-optimizer` | App Store Optimizer | ASO, ratings, keyword strategy |
| `marketing-baidu-seo-specialist` | Baidu SEO Specialist | Baidu search optimization, China SEO |
| `marketing-bilibili-content-strategist` | Bilibili Content Strategist | Bilibili platform, video content for Chinese audiences |
| `marketing-book-co-author` | Book Co-Author | Book writing, structure, chapter development |
| `marketing-carousel-growth-engine` | Carousel Growth Engine | Social media carousels, engagement, virality |
| `marketing-china-ecommerce-operator` | China E-Commerce Operator | Tmall, JD.com, Chinese e-commerce operations |
| `marketing-china-market-localization-strategist` | China Market Localization Strategist | Adapting products and messaging for China |
| `marketing-content-creator` | Content Creator | Blog posts, articles, content strategy |
| `marketing-cross-border-ecommerce` | Cross-Border E-Commerce | International shipping, multi-currency, localization |
| `marketing-douyin-strategist` | Douyin Strategist | Douyin (Chinese TikTok) content and growth |
| `marketing-email-strategist` | Email Strategist | Email campaigns, sequences, deliverability |
| `marketing-global-podcast-strategist` | Global Podcast Strategist | Podcast growth, international audiences |
| `marketing-growth-hacker` | Growth Hacker | Viral loops, A/B testing, acquisition funnels |
| `marketing-instagram-curator` | Instagram Curator | Instagram content, aesthetics, growth |
| `marketing-kuaishou-strategist` | Kuaishou Strategist | Kuaishou short video platform strategy |
| `marketing-linkedin-content-creator` | LinkedIn Content Creator | LinkedIn thought leadership, B2B content |
| `marketing-livestream-commerce-coach` | Livestream Commerce Coach | Live selling, viewer conversion, streaming commerce |
| `marketing-multi-platform-publisher` | Multi-Platform Publisher | Cross-platform content distribution |
| `marketing-podcast-strategist` | Podcast Strategist | Podcast production, growth, monetization |
| `marketing-pr-communications-manager` | PR / Communications Manager | Press releases, media relations, brand reputation |
| `marketing-private-domain-operator` | Private Domain Operator | WeChat ecosystem, private traffic, CRM |
| `marketing-reddit-community-builder` | Reddit Community Builder | Reddit engagement, community management |
| `marketing-seo-specialist` | SEO Specialist | Technical SEO, content optimization, link building |
| `marketing-short-video-editing-coach` | Short Video Editing Coach | Short-form video production and editing |
| `marketing-social-media-strategist` | Social Media Strategist | Cross-platform social strategy |
| `marketing-tiktok-strategist` | TikTok Strategist | TikTok content, trends, creator growth |
| `marketing-twitter-engager` | Twitter Engager | Twitter/X engagement and community building |
| `marketing-video-optimization-specialist` | Video Optimization Specialist | YouTube SEO, video performance |
| `marketing-wechat-official-account` | WeChat Official Account | WeChat OA content and growth |
| `marketing-weibo-strategist` | Weibo Strategist | Weibo platform content and engagement |
| `marketing-x-twitter-intelligence-analyst` | X/Twitter Intelligence Analyst | Social listening, sentiment, competitive intel |
| `marketing-xiaohongshu-specialist` | Xiaohongshu Specialist | Little Red Book (RED) content strategy |
| `marketing-zhihu-strategist` | Zhihu Strategist | Zhihu Q&A platform, thought leadership |

### Paid Media (7 agents)
| Slug | Name | Description |
|------|------|-------------|
| `paid-media-auditor` | Paid Media Auditor | Ad account audits, waste identification |
| `paid-media-creative-strategist` | Creative Strategist | Ad creative strategy, testing frameworks |
| `paid-media-paid-social-strategist` | Paid Social Strategist | Facebook, Instagram, TikTok paid campaigns |
| `paid-media-ppc-strategist` | PPC Strategist | Google/Bing paid search, bidding, ROI |
| `paid-media-programmatic-buyer` | Programmatic Buyer | DSPs, display, programmatic buying |
| `paid-media-search-query-analyst` | Search Query Analyst | Search term mining, negative keywords |
| `paid-media-tracking-specialist` | Tracking Specialist | Pixel setup, GTM, attribution, analytics |

### Product (5 agents)
| Slug | Name | Description |
|------|------|-------------|
| `product-behavioral-nudge-engine` | Behavioral Nudge Engine | Behavior change, nudge theory, product psychology |
| `product-feedback-synthesizer` | Feedback Synthesizer | User feedback analysis, theme extraction |
| `product-manager` | Product Manager | Roadmaps, PRDs, prioritization, stakeholder management |
| `product-sprint-prioritizer` | Sprint Prioritizer | Sprint planning, backlog grooming, velocity |
| `product-trend-researcher` | Trend Researcher | Market trends, competitive landscape, opportunity mapping |

### Project Management (7 agents)
| Slug | Name | Description |
|------|------|-------------|
| `project-management-experiment-tracker` | Experiment Tracker | A/B test tracking, experiment documentation |
| `project-management-jira-workflow-steward` | Jira Workflow Steward | Jira configuration, workflow design, project hygiene |
| `project-management-meeting-notes-specialist` | Meeting Notes Specialist | Meeting summaries, action items, follow-ups |
| `project-management-project-shepherd` | Project Shepherd | Project health monitoring, risk tracking |
| `project-management-studio-operations` | Studio Operations | Studio workflow, resource management, scheduling |
| `project-management-studio-producer` | Studio Producer | Creative project production, milestone tracking |
| `project-manager-senior` | Senior Project Manager | Stakeholder management, delivery, complex projects |

### Sales (9 agents)
| Slug | Name | Description |
|------|------|-------------|
| `sales-account-strategist` | Account Strategist | Account planning, expansion, relationship management |
| `sales-coach` | Sales Coach | Sales skills development, call coaching, objection handling |
| `sales-deal-strategist` | Deal Strategist | Deal strategy, competitive positioning, closing |
| `sales-discovery-coach` | Discovery Coach | Discovery call frameworks, qualification |
| `sales-engineer` | Sales Engineer | Technical presales, demos, solution design |
| `sales-offer-lead-gen-strategist` | Offer & Lead Gen Strategist | Lead generation offers, funnel strategy |
| `sales-outbound-strategist` | Outbound Strategist | Cold outreach, sequences, pipeline building |
| `sales-pipeline-analyst` | Pipeline Analyst | Pipeline analysis, forecasting, CRM hygiene |
| `sales-proposal-strategist` | Proposal Strategist | RFP responses, proposal writing, win strategy |

### Security (10 agents)
| Slug | Name | Description |
|------|------|-------------|
| `security-appsec-engineer` | AppSec Engineer | Application security, SAST/DAST, secure code review |
| `security-architect` | Security Architect | Security architecture, zero trust, threat modeling |
| `security-blockchain-security-auditor` | Blockchain Security Auditor | Smart contract auditing, DeFi security |
| `security-cloud-security-architect` | Cloud Security Architect | AWS/GCP/Azure security, IAM, cloud controls |
| `security-compliance-auditor` | Compliance Auditor | SOC2, ISO27001, GDPR, audit readiness |
| `security-incident-responder` | Incident Responder | Breach response, forensics, containment |
| `security-penetration-tester` | Penetration Tester | Authorized pen testing, red team operations |
| `security-senior-secops` | Senior SecOps | Security operations, SIEM, detection engineering |
| `security-threat-detection-engineer` | Threat Detection Engineer | Detection rules, threat hunting, EDR |
| `security-threat-intelligence-analyst` | Threat Intelligence Analyst | Threat actor research, IOCs, intelligence reports |

### Spatial Computing (6 agents)
| Slug | Name | Description |
|------|------|-------------|
| `macos-spatial-metal-engineer` | macOS Spatial Metal Engineer | Metal GPU programming, spatial computing on macOS |
| `terminal-integration-specialist` | Terminal Integration Specialist | Terminal tooling, shell integrations |
| `visionos-spatial-engineer` | visionOS Spatial Engineer | Apple Vision Pro, RealityKit, SwiftUI volumes |
| `xr-cockpit-interaction-specialist` | XR Cockpit Interaction Specialist | Spatial UI for vehicle/cockpit environments |
| `xr-immersive-developer` | XR Immersive Developer | WebXR, immersive experiences, VR/AR dev |
| `xr-interface-architect` | XR Interface Architect | Spatial interface design, XR patterns |

### Specialized (53 agents)
| Slug | Name | Description |
|------|------|-------------|
| `accounts-payable-agent` | Accounts Payable Agent | AP processing, vendor payments, invoice management |
| `agentic-identity-trust` | Agentic Identity & Trust | Agent authentication, trust frameworks |
| `agents-orchestrator` | Agents Orchestrator | Multi-agent coordination, task delegation |
| `automation-governance-architect` | Automation Governance Architect | AI governance, automation policy, compliance |
| `business-strategist` | Business Strategist | Strategy frameworks, competitive analysis, growth planning |
| `change-management-consultant` | Change Management Consultant | Organizational change, adoption, training |
| `chief-financial-officer` | Chief Financial Officer | CFO-level financial strategy and oversight |
| `corporate-training-designer` | Corporate Training Designer | L&D programs, curriculum design, e-learning |
| `customer-service` | Customer Service | Customer support, resolution, satisfaction |
| `customer-success-manager` | Customer Success Manager | Onboarding, retention, expansion, health scores |
| `data-consolidation-agent` | Data Consolidation Agent | Data merging, deduplication, master data management |
| `data-privacy-officer` | Data Privacy Officer | Privacy by design, GDPR/CCPA, data mapping |
| `esg-sustainability-officer` | ESG / Sustainability Officer | ESG reporting, sustainability strategy |
| `government-digital-presales-consultant` | Government Digital Presales Consultant | Public sector sales, RFP, government procurement |
| `grant-writer` | Grant Writer | Grant proposals, funding applications |
| `healthcare-customer-service` | Healthcare Customer Service | Patient communication, HIPAA-aware support |
| `healthcare-marketing-compliance` | Healthcare Marketing Compliance | FDA/FTC-compliant healthcare marketing |
| `hospitality-guest-services` | Hospitality Guest Services | Hotel/hospitality guest experience |
| `hr-onboarding` | HR Onboarding | Employee onboarding, documentation, welcome experience |
| `identity-graph-operator` | Identity Graph Operator | Identity resolution, customer data unification |
| `language-translator` | Language Translator | Translation, localization, cultural adaptation |
| `legal-billing-time-tracking` | Legal Billing & Time Tracking | Legal billing, matter management, time entry |
| `legal-client-intake` | Legal Client Intake | Client intake, conflict checks, matter opening |
| `legal-document-review` | Legal Document Review | Contract review, redlining, legal analysis |
| `loan-officer-assistant` | Loan Officer Assistant | Mortgage origination, loan structuring |
| `lsp-index-engineer` | LSP Index Engineer | Language Server Protocol, code indexing |
| `ma-integration-manager` | M&A Integration Manager | Post-merger integration, synergy realization |
| `medical-billing-coding-specialist` | Medical Billing & Coding Specialist | ICD-10, CPT codes, medical billing |
| `operations-manager` | Operations Manager | Ops efficiency, process design, KPI tracking |
| `organizational-psychologist` | Organizational Psychologist | Team dynamics, culture, org design |
| `personal-growth-mentor` | Personal Growth Mentor | Coaching, goal setting, habit formation |
| `real-estate-buyer-seller` | Real Estate Buyer/Seller Agent | Property transactions, negotiation, market analysis |
| `recruitment-specialist` | Recruitment Specialist | Sourcing, interviewing, hiring process |
| `report-distribution-agent` | Report Distribution Agent | Automated reporting, distribution workflows |
| `retail-customer-returns` | Retail Customer Returns | Returns processing, refunds, exchange policy |
| `sales-data-extraction-agent` | Sales Data Extraction Agent | CRM data extraction, sales analytics |
| `sales-outreach` | Sales Outreach Agent | Outreach templates, sequences, personalization |
| `specialized-chief-of-staff` | Chief of Staff | Executive support, cross-functional coordination |
| `specialized-civil-engineer` | Civil Engineer | Civil engineering analysis and design guidance |
| `specialized-cultural-intelligence-strategist` | Cultural Intelligence Strategist | Cross-cultural communication, global teams |
| `specialized-developer-advocate` | Developer Advocate | DevRel, developer community, technical content |
| `specialized-document-generator` | Document Generator | Automated document creation, templates |
| `specialized-french-consulting-market` | French Consulting Market Specialist | French business culture, consulting market |
| `specialized-korean-business-navigator` | Korean Business Navigator | Korean market, business culture, B2B relations |
| `specialized-mcp-builder` | MCP Builder | Building Model Context Protocol servers and tools |
| `specialized-model-qa` | Model QA Specialist | LLM evaluation, model quality assurance |
| `specialized-pricing-analyst` | Pricing Analyst | Pricing strategy, competitive pricing, elasticity |
| `specialized-salesforce-architect` | Salesforce Architect | Salesforce design, Apex, integrations |
| `specialized-strategy-duel-agent` | Strategy Duel Agent | Red team / blue team strategy debates |
| `specialized-workflow-architect` | Workflow Architect | Process automation, workflow design |
| `study-abroad-advisor` | Study Abroad Advisor | International education, visa, application guidance |
| `supply-chain-strategist` | Supply Chain Strategist | Supply chain optimization, risk, logistics |
| `zk-steward` | ZK Steward | Zero-knowledge proofs, ZK protocol design |

### Support (6 agents)
| Slug | Name | Description |
|------|------|-------------|
| `support-analytics-reporter` | Analytics Reporter | Reporting automation, dashboard generation |
| `support-executive-summary-generator` | Executive Summary Generator | Concise executive summaries from long documents |
| `support-finance-tracker` | Finance Tracker | Expense tracking, budget monitoring |
| `support-infrastructure-maintainer` | Infrastructure Maintainer | Server maintenance, patching, uptime |
| `support-legal-compliance-checker` | Legal Compliance Checker | Contract compliance, regulatory checks |
| `support-support-responder` | Support Responder | Ticket responses, support workflows |

### Testing (8 agents)
| Slug | Name | Description |
|------|------|-------------|
| `testing-accessibility-auditor` | Accessibility Auditor | WCAG audits, assistive technology testing |
| `testing-api-tester` | API Tester | REST/GraphQL testing, contract testing |
| `testing-evidence-collector` | Evidence Collector | Test evidence documentation, screenshots |
| `testing-performance-benchmarker` | Performance Benchmarker | Load testing, benchmarking, profiling |
| `testing-reality-checker` | Reality Checker | Verifying claims against reality, assumptions |
| `testing-test-results-analyzer` | Test Results Analyzer | Test report analysis, failure triage |
| `testing-tool-evaluator` | Tool Evaluator | Evaluating and comparing tools and libraries |
| `testing-workflow-optimizer` | Workflow Optimizer | Testing workflow efficiency, automation |

---

## Common Multi-Agent Workflows

### Feature Development
```
1. Product Manager    → write PRD and acceptance criteria
2. UX Researcher      → validate requirements with user lens
3. UI Designer        → create design specs
4. Frontend Developer → implement UI
5. Backend Architect  → design API
6. Code Reviewer      → review implementation
7. Testing API Tester → write and run tests
8. Reality Checker    → verify feature is production-ready
```

### Security Audit
```
1. Security AppSec Engineer       → static analysis of codebase
2. Security Penetration Tester    → dynamic testing and exploits
3. Security Architect             → threat model review
4. Engineering Code Reviewer      → secure code review
5. Security Compliance Auditor    → compliance gap analysis
```

### Marketing Campaign
```
1. Product Trend Researcher       → market and competitor research
2. Business Strategist            → positioning and messaging
3. Marketing Content Creator      → draft content
4. Marketing SEO Specialist       → optimize for search
5. Marketing Social Media Strategist → distribution plan
6. Paid Media Creative Strategist → paid amplification
```

### Incident Response
```
1. Engineering Incident Response Commander → triage and coordinate
2. Engineering SRE                         → diagnose and remediate
3. Security Incident Responder             → rule out security breach
4. Engineering Technical Writer            → write postmortem
```

---

## Tips

- **Be explicit**: naming the agent gets you the right specialist immediately.
- **Chain naturally**: end one agent's output with "hand off to [agent]" to continue.
- **See examples**: `agency-agents/examples/` has complete multi-agent workflow walkthroughs.
- **Strategy playbooks**: `agency-agents/strategy/playbooks/` covers 7 project phases.
- **Source agents**: `agency-agents/` contains the original `.md` files to browse or edit.
