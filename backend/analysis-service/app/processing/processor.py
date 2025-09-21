import logging
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, List

from ..agent.agent import create_analysis_agents, AgentRunner
from ..config.settings import settings
from ..utils.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)


class AnalysisProcessor:
    def __init__(self):
        self.max_workers = settings.service.max_workers
        self.timeout = settings.service.timeout_seconds
        self.agent_runner = AgentRunner(
            app_name=settings.agent.app_name,
            user_id=settings.agent.user_id,
            session_id_prefix=settings.agent.session_id_prefix
        )
        self.pdf_generator = PDFGenerator()

    async def process_analysis_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process analysis request with sections processed sequentially"""
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Processing analysis request {request_id} for startup: {request_data.get('startup_name')}")
        
        try:
            rag_corpus = request_data['rag_corpus']
            startup_name = request_data['startup_name']
            upload_id = request_data['upload_id']
            print(upload_id)
            gcp_bucket = settings.gcp.bucket_name
            
            sections = self._define_analysis_sections(startup_name)
            
            # Process sections sequentially (one at a time)
            results = {}
            for section in sections:
                logger.info(f"Processing section: {section['name']} for {startup_name}")
                try:
                    result = await self._process_section_async(
                        rag_corpus,
                        startup_name,
                        section['name'],
                        section['prompt']
                    )
                    results[section['name']] = result
                    logger.info(f"Completed section: {section['name']}")
                except Exception as e:
                    logger.error(f"Error processing section {section['name']}: {str(e)}")
                    results[section['name']] = {"error": str(e)}

            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # Prepare analysis data for PDF generation
            analysis_data = {
                "request_id": request_id,
                "service_name": "analysis_service",
                "startup_name": startup_name,
                "gcp_bucket": gcp_bucket,
                "upload_id": upload_id,
                "status": "completed",
                "timestamp": end_time.isoformat(),
                "processing_time_seconds": processing_time,
                "results": results,
                "sections_processed": len(results),
                "successful_sections": len([r for r in results.values() if "error" not in r])
            }
            
            # Generate PDF and upload to cloud storage
            try:
                logger.info(f"Generating PDF report for {startup_name}")
                pdf_url = self.pdf_generator.process_analysis_to_pdf_url(analysis_data, gcp_bucket,upload_id)
                analysis_data["pdf_url"] = pdf_url
                logger.info(f"PDF report generated and uploaded: {pdf_url}")
            except Exception as e:
                logger.error(f"Failed to generate PDF report: {str(e)}")
                analysis_data["pdf_error"] = str(e)
                # Continue without PDF - don't fail the entire process
            
            return analysis_data

        except Exception as e:
            logger.error(f"Failed to process analysis request {request_id}: {str(e)}")
            return {
                "request_id": request_id,
                "startup_name": request_data.get('startup_name', 'unknown'),
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    def _define_analysis_sections(self, startup_name: str) -> List[Dict[str, str]]:
        """Define the analysis sections to be processed"""
        return [
           {
                "name": "company_overview",
                "prompt": f"""You are a research assistant generating a structured company overview {startup_name}. Use only the information retrieved from the RAG tool. Do not add assumptions, estimates, or invented details. If information is missing, leave it blank instead of fabricating.
                Add details like Facilities, Office details/Plant details, Warehousesi, Valuation and others.
					Structure the output in markdown as follows:
					1. One or two Paragraph overview of the company
					2. Vision & Mission: As explicitly stated by the company
					Only include content supported by retrieved data.
				"""
            },
            {
                "name": "founding_team",
                "prompt": f"""Generating a structured Founding Team section at {startup_name}. Use only the information retrieved from the RAG tool. Do not add assumptions or invent details. If data is missing, skip that founder.
					Format the output in bullet points as follows:
						Founder Name, Position: Prior experience and a brief description of the founder (maximum 5 lines).
					Example format:
					## Founding Team
					- **John Doe, CEO**: Former Product Head at XYZ Corp. with 10+ years of SaaS experience. Previously founded ABC Tech, which was acquired by QRS Ltd. Recognized for expertise in scaling enterprise products.  
					- **Jane Smith, CTO**: Ex-Senior Engineer at Google. Specialized in distributed systems and AI/ML. Holds multiple patents and has led engineering teams of 50+.  
				"""
            },
            {
                "name": "problem_statement",
                "prompt": f"""Generating a structured Problem Statement section conating what startup is solving {startup_name}. Make the section very detailed, factually grounded, and comprehensive (1 ~ 5 pages) — expanding wherever RAG provides data, but never hallucinating beyond what is retrieved.
				Primary Source: Use the RAG tool for all available company-specific information.
				Secondary Source: If key details are missing, you may use the Web Search tool, but clearly state only factual information.
				Do not hallucinate. If data is not available, skip instead of fabricating.

				Format the output in Markdown with the following structure:
				## Problem Statement

				### Detailed Problem Explanation
				A descriptive paragraph (3–6 sentences) explaining the core problem faced by the target market, using company and industry context.

				### The Category Problem
				
                - Point 1  
				- Point 2  
				- Point 3  

				### Current Alternatives
				
                - **Alternative 1**: Detailed explanation (2–3 sentences)  
				- **Alternative 2**: Detailed explanation (2–3 sentences)  
				- **Alternative 3**: Detailed explanation (2–3 sentences)  

				### Why Now
				Explaining Market Trends, Competitive Edge, Urgency/Opportunity, market timing, shifts, or accelerators (e.g., regulatory changes, tech adoption, remote work trends).  
				
                - Point 1  
				- Point 2  
				- Point 3  
				"""
            },
            {
                "name": "Solution",
                "prompt": f"""Generating a structured Solution section conating what is the solution given by startup {startup_name}. Make the section very detailed, factually grounded, and comprehensive (1 ~ 5 pages)— expanding wherever RAG provides data, but never hallucinating beyond what is retrieved.
				Primary Source: Use the RAG tool for all available company-specific information.
				Secondary Source: If key details are missing, you may use the Web Search tool, but clearly state only factual information.
				Do not hallucinate. If data is not available, skip instead of fabricating.
				Format the output in Markdown with the following structure:
				## SOLUTION

				### Product Description
				A descriptive paragraph (3–6 sentences) explaining the product of the startup which is problem faced by the target market, using company and industry context. 
				
				Different features offered by product
				
                - **Point 1**: Detailed explanation (2–3 sentences)  
				- **Point 2**: Detailed explanation (2–3 sentences)  
				- **Point 3**: Detailed explanation (2–3 sentences)  				
				

				### What <Startup Product> Replaces
				
                - **Point 1**: Detailed explanation (2–3 sentences)  
				- **Point 2**: Detailed explanation (2–3 sentences)  
				- **Point 3**: Detailed explanation (2–3 sentences)  

				### Competitive Landscape and Advantages
				
                - **Point 1**: Detailed explanation (2–3 sentences)  
				- **Point 2**: Detailed explanation (2–3 sentences)  
				- **Point 3**: Detailed explanation (2–3 sentences)  
				"""
            },
            {
                "name": "Market_Opportunity",
                "prompt": f"""Generating a structured Market Opportunity section of startup {startup_name}. Make the section very detailed, factually grounded, and comprehensive (1 ~ 5 pages) — expanding wherever RAG provides data, but never hallucinating beyond what is retrieved.
				Use RAG tool first for company-specific and sector-specific data.
				Use Web Search tool to supplement more details. Only rely on trusted sources (e.g., Gartner, McKinsey, Statista, Deloitte, World Bank, IMF, government sites, major financial newspapers).
				Do not hallucinate. If data is unavailable, leave that part blank instead of fabricating.
				
				Format the output in Markdown with the following structure:
				## Market Opportunity

				### Overview
				A detailed paragraph (3–5 sentences) explaining the size and importance of the market, key growth drivers, and relevance to the company.

				### Market Size & Growth
				
                - Point 1 (e.g., Global market size, CAGR, TAM/SAM/SOM if available)  
				- Point 2 (e.g., Regional/sector-specific opportunity)  
				- Point 3 (e.g., relevant adoption or expansion trends)  

				### Key Market Drivers
				
                - Point 1  
				- Point 2  
				- Point 3  

				### Subsections (Dynamic)
				If retrieved data provides insights, include subsections like:
				
                - **Regional Opportunity** (if geography-specific data available)  
				- **Customer Segments** (enterprise, SMB, etc.)  
				- **Regulatory Tailwinds** (if industry-specific policies are driving adoption)  
				- **Technology Enablers** (if AI/automation/infra are enabling the market)  
				"""
            },
            {
                "name": "Business_Model",
                "prompt": f"""Generating a structured Business Model section of {startup_name}. Make the section very detailed, factually grounded, and comprehensive (1 ~ 5 pages) — expanding wherever RAG provides data, but never hallucinating beyond what is retrieved.
				Consider data from Current Revenue Streams from Service Offering, 
                Primary Source: Use RAG tool for company-specific details.
				Secondary Source: If needed, use Web Search tool, but rely only on trusted sources (official company website, investor reports, reputed news/media, consulting reports).
				Do not hallucinate. If data is missing, leave the field blank instead of fabricating.
				
				Format the output in Markdown with the following structure:
				## Business Model

				### Model Narrative

				| Item                     | Details |
				|--------------------------|---------|
				| Revenue Model            | ... |
				| Average Contract Value   | ... |
				| Revenue Growth           | ... |
				| Gross Margins            | ... |
				| LTV                      | ... |
				| LTV : CAC Ratio          | ... |
				| Refund Policy            | ... |
				| Geographic Revenue Split | ... |

                ### Current Revenue Streams from Service Offering
                
                #### Streams 1 
                
                - **Name of the Revenue Stream**
                - **Description**
                - **Target Audience**
                - **Percentage Contribution**
                
                #### Streams 2
                
                - **Name of the Revenue Stream**
                - **Description**
                - **Target Audience**
                - **Percentage Contribution**

				### Pricing Strategy
				A short descriptive paragraph (3–5 sentences) explaining the core revenue mechanics.  
				
                #### Outline the pricing models and tiers
                
                - Point 1 (e.g., for Academic Institutions & Students)  
				- Point 2 (e.g., for Corporates)  
				- Point 3 (e.g., upsell through advanced analytics modules)  
				If available, add a table for pricing tiers, user-based pricing, or additional monetization channels.  

				### Scalability of Revenue Model
				
                - Highlight 1 (e.g., retention rate, ARR milestones)  
				- Highlight 2 (e.g., enterprise wins, global expansion)  
				- Highlight 3 (e.g., notable partnerships, cost efficiency)  

				### Looking Ahead
				2–3 sentences projecting how the business model will evolve (e.g., scaling internationally, expanding into new verticals, ARPU improvements).  
				"""
            },
            {
                "name": "Market_Opportunity",
                "prompt": f"""Generating a structured Market Opportunity section of startup {startup_name}. Create subsections only if the data is avaibale. Make the section very detailed, factually grounded, and comprehensive (1 ~ 5 pages) — expanding wherever RAG provides data, but never hallucinating beyond what is retrieved.
				Consider Competitor Analysis, Combined Market Opportunity, Industry Reports, Market Sizing
                Use RAG tool for company-specific and sector-specific data.
				Use Web Search tool to supplement more details. Only rely on trusted sources (e.g., Gartner, McKinsey, Statista, Deloitte, World Bank, IMF, government sites, major financial newspapers).
				Do not hallucinate. If data is unavailable, leave that part blank instead of fabricating.
				
				Format the output in Markdown with the following structure:
				## Market Opportunity

				### Overview
				A detailed paragraph (3–5 sentences) explaining the size and importance of the market, key growth drivers, and relevance to the company.

				### Market Size & Growth
				
                - Point 1 (e.g., Global market size, CAGR, TAM/SAM/SOM if available)  
				- Point 2 (e.g., Regional/sector-specific opportunity)  
				- Point 3 (e.g., relevant adoption or expansion trends)  

				### Key Market Drivers
				
                - Point 1  
				- Point 2  
				- Point 3  

				### Subsection Name (Dynamic)
				If retrieved data provides insights, include subsections like:
				
                - **Regional Opportunity** (if geography-specific data available)  
				- **Customer Segments** (enterprise, SMB, etc.)  
				- **Regulatory Tailwinds** (if industry-specific policies are driving adoption)  
				- **Technology Enablers** (if AI/automation/infra are enabling the market)  
				"""
            },
            {
                "name": "traction",
                "prompt": f"""You are a research assistant generating a structured Traction section of {startup_name}. Create subsections only if the data is available. 
				Primary Source: Use RAG tool for all available company-specific details.
				Secondary Source: If details are missing, use Web Search tool, but only rely on trusted sources (official company website, press releases, reputable media, consulting reports).
				Do not hallucinate. If data is not available, skip instead of fabricating.
				
				Format the output in Markdown as follows: 
				## Traction

				### Overview
				A short paragraph (3–5 sentences) summarizing the company’s progress in terms of users, clients, revenue, adoption, or recognition.

				### Key Metrics
				
                - Metric 1 (e.g., paid users, ARR, retention rate)  
				- Metric 2 (e.g., enterprise customers, sectors served)  
				- Metric 3 (e.g., gross margins, profitability, growth rate)  
				- Metric 4 (e.g., partnerships, funding milestones)  

				#### Customers & Adoption (include if data is available)
				
                - Detail 1  
				- Detail 2  

				#### Financial Performance (include if data is available)
				
                - Detail 1  
				- Detail 2  

				#### Partnerships & Recognition (include if data is available)
				
                - Detail 1  
				- Detail 2  
				"""
            },
            {
                "name": "Go_to_market",
                "prompt": f"""You are a research assistant generating a structured Go-To-Market Strategy section of {startup_name}.
				Use only information retrieved from the RAG tool.
				Do not fabricate or assume details. If a subsection has no data, omit it.
				
				Format the output in Markdown as follows: 
				## Go-To-Market Strategy

				### Overview
				A short descriptive paragraph (3–5 sentences) summarizing the company’s GTM approach.

				### Distribution Channels
				
                - Point 1 (e.g., direct sales, partnerships, inbound/outbound)  
				- Point 2  
				- Point 3  

				### Target Segments
				
                - Segment 1 (e.g., enterprise clients, SMBs, industry verticals)  
				- Segment 2  

				### GTM Tactics
				
                - Point 1 (e.g., founder-led sales, CXO roundtables, channel partners)  
				- Point 2 (e.g., inbound marketing, partnerships)  
				- Point 3  

				### Expansion Plans
				A short paragraph (2–3 sentences) highlighting regional or international GTM moves.
				"""
            },
            {
                "name": "deal_details",
                "prompt": f"""You are a research assistant generating a structured Deal Details section of {startup_name}.
				Use only information retrieved from the RAG tool.
				Do not fabricate missing data. If data is unavailable, skip the field.
				
				Format the output in Markdown as follows: 
				## Deal Details

				### Current Round

				- Amount seeking to raise: …  
				- Purpose of the raise: …  
				- Expected valuation (if available): …  

				### Previous Funding

				- Round type: …  
				- Amount raised: …  
				- Investors (if available): …  
				- Date of raise: …  
				"""
            },
            {
                "name": "risk_challenges",
                "prompt": f"""You are a research assistant generating a structured Risks & Challenges section of {startup_name}.
				Use only information retrieved from the RAG tool.
				Do not fabricate.
				Structure output in a Markdown table with 3 columns: Risk | Description | Mitigant.
				
				Format the output in Markdown as follows: 
				## Risks & Challenges

				| Risk | Description | Mitigant |
				|------|-------------|-----------|
				| Risk 1 | Short explanation (1–2 sentences) | Mitigation strategy (1–2 sentences) |
				| Risk 2 | … | … |
				| Risk 3 | … | … |

				"""
            }
        ]

    async def _process_section_async(self, rag_corpus: str, startup_name: str, section_name: str, prompt: str) -> Dict[str, Any]:
        """Process a single analysis section asynchronously"""
        try:
            logger.info(f"Processing section: {section_name} for {startup_name}")
            
            agent = create_analysis_agents(rag_corpus, settings.service.model_name)
            
            formatted_prompt = f"""
            Section: {section_name}
            Startup: {startup_name}
            
            {prompt}
            
            Please provide a detailed analysis with proper citations and sources.
            Format the response in markdown with clear sections and bullet points where appropriate.
            """
            
            result = await self.agent_runner.call_agent_async(formatted_prompt, agent)
            
            return {
                "section": section_name,
                "content": result,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing section {section_name}: {str(e)}")
            return {
                "section": section_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
