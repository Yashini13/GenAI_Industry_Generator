 pip install streamlit requests
%%writefile app.py
import os
import re
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ResearchResult:
    industry_info: str
    company_info: str

@dataclass
class Resource:
    title: str
    description: str
    link: str
    category: str
    format: str

class IndustryResearchAgent:
    def __init__(self, industry: str, company_name: str):
        self.industry = industry
        self.company_name = company_name
        self.api_key = "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"

        if not self.api_key:
            raise ValueError("TAVILY_API_KEY environment variable not set")

    def research_industry(self) -> str:
        try:
            url = "https://api.tavily.com/search"
            params = {
                "query": f"{self.industry} industry AI applications",
                "api_key": self.api_key,
                "search_depth": "advanced",
                "include_answer": True
            }
            response = requests.post(url, json=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if not results:
                return f"No data found for {self.industry}"

            # Try to get the answer first, fall back to the first result's text
            return data.get("answer") or results[0].get("text", f"No data found for {self.industry}")

        except requests.RequestException as e:
            return f"Error researching industry: {str(e)}"

    def research_company(self) -> str:
        try:
            url = "https://api.tavily.com/search"
            params = {
                "query": f"{self.company_name} AI ML use cases",
                "api_key": self.api_key,
                "search_depth": "advanced",
                "include_answer": True
            }
            response = requests.post(url, json=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if not results:
                return f"No data found for {self.company_name}"

            return data.get("answer") or results[0].get("text", f"No data found for {self.company_name}")

        except requests.RequestException as e:
            return f"Error researching company: {str(e)}"

    def get_results(self) -> ResearchResult:
        return ResearchResult(
            industry_info=self.research_industry(),
            company_info=self.research_company()
        )

class UseCaseGenerationAgent:
    def __init__(self, industry_info: str, company_info: str):
        self.industry_info = industry_info
        self.company_info = company_info
        self.api_key = "AIzaSyBWjtSlzszul1CG_O_H_CKWjB4tVAKGXeY"

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

    def generate_use_cases(self) -> List[str]:
        try:
            prompt = f"""
            Based on the following information:
            Industry: {self.industry_info}
            Company: {self.company_info}

            Generate 5 specific and actionable AI/GenAI use cases.
            Format each use case as a single line item.
            """

            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1000,
                    "topP": 0.8,
                    "topK": 40
                }
            }

            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()


            if not data:
                return ["Error: Empty response from API"]

            candidates = data.get("candidates", [])
            if not candidates:
                return ["Error: No candidates in response"]

            first_candidate = candidates[0]
            if not first_candidate:
                return ["Error: Empty first candidate"]

            content = first_candidate.get("content", {})
            if not content:
                return ["Error: No content in candidate"]

            parts = content.get("parts", [])
            if not parts:
                return ["Error: No parts in content"]

            text = parts[0].get("text", "")
            if not text:
                return ["Error: No text in first part"]

            # Split the text into lines and clean them up
            use_cases = [line.strip() for line in text.split("\n") if line.strip()]

            # If we got no use cases after processing, return an error
            if not use_cases:
                return ["No use cases generated"]

            return use_cases

        except requests.RequestException as e:
            return [f"Error generating use cases: {str(e)}"]
        except KeyError as e:
            return [f"Error parsing API response: {str(e)}"]
        except Exception as e:
            return [f"Unexpected error: {str(e)}"]

class ResourceAssetCollectionAgent:
    def __init__(self, use_cases: List[str]):
        self.use_cases = use_cases
        self.base_url = "https://api.us.socrata.com/api/catalog/v1"

    def get_resources(self) -> List[Resource]:
        all_resources = []

        for use_case in self.use_cases:
            try:
                params = {
                    'q': use_case,
                    'only': 'datasets',
                    'limit': 5
                }

                response = requests.get(
                    self.base_url,
                    params=params,
                    headers={'Accept': 'application/json'},
                    timeout=10
                )
                response.raise_for_status()

                data = response.json()
                resources = [
                    Resource(
                        title=result.get('resource', {}).get('name', 'Untitled'),
                        description=result.get('resource', {}).get('description', 'No description'),
                        link=result.get('resource', {}).get('permalink', '#'),
                        category=result.get('classification', {}).get('domain_category', 'Uncategorized'),
                        format=result.get('resource', {}).get('format', 'Unknown')
                    )
                    for result in data.get('results', [])
                ]
                all_resources.extend(resources)

            except requests.RequestException as e:
                print(f"Error fetching resources for '{use_case}': {str(e)}")
                continue

        return all_resources

def create_markdown_report(
    company_name: str,
    industry: str,
    industry_info: str,
    company_info: str,
    use_cases: List[str],
    resources: List[Resource]
) -> str:
    markdown_content = f"""# AI and GenAI Proposal for {company_name} in the {industry} Industry

## Industry Overview
{industry_info}

## Company Overview
{company_info}

## Potential AI and GenAI Use Cases
"""

    for i, use_case in enumerate(use_cases, 1):
        markdown_content += f"{i}. {use_case}\n"

    markdown_content += "\n## Relevant Datasets and Resources\n"

    for i, resource in enumerate(resources, 1):
        markdown_content += f"""{i}. **{resource.title}**
   - Description: {resource.description}
   - Category: {resource.category}
   - Format: {resource.format}
   - [Access Resource]({resource.link})
"""

    return markdown_content

def markdown_to_text(markdown_content: str) -> str:
    # Remove headers
    text = re.sub(r'#.*\n', '', markdown_content)
    # Remove bold and italics
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    # Remove links
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Clean up formatting
    text = re.sub(r'\*\s', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def generate_report(company_name: str, industry: str) -> tuple[str, str]:
    try:
        # Step 1: Research
        research_agent = IndustryResearchAgent(industry, company_name)
        research_results = research_agent.get_results()

        # Step 2: Generate Use Cases
        use_case_agent = UseCaseGenerationAgent(
            research_results.industry_info,
            research_results.company_info
        )
        use_cases = use_case_agent.generate_use_cases()

        # Step 3: Collect Resources
        resource_agent = ResourceAssetCollectionAgent(use_cases)
        resources = resource_agent.get_resources()

        # Step 4: Create Reports
        markdown_content = create_markdown_report(
            company_name,
            industry,
            research_results.industry_info,
            research_results.company_info,
            use_cases,
            resources
        )

        plain_text = markdown_to_text(markdown_content)

        return markdown_content, plain_text

    except Exception as e:
        return f"Error generating report: {str(e)}", f"Error generating report: {str(e)}"

# Streamlit Interface
import streamlit as st

def main():
    st.set_page_config(page_title="AI & GenAI Use Case Generator", layout="wide")

    st.title("AI & GenAI Use Case Generator")
    st.write("Generate AI and GenAI use cases and resources for your industry and company.")

    with st.form("input_form"):
        company_name = st.text_input("Company Name")
        industry = st.text_input("Industry")
        submitted = st.form_submit_button("Generate Report")

    if submitted and company_name and industry:
        with st.spinner("Generating report..."):
            try:
                markdown_content, plain_text = generate_report(company_name, industry)


                with open("AI_GenAI_Proposal.md", "w") as f:
                    f.write(markdown_content)
                with open("AI_GenAI_Proposal_PlainText.txt", "w") as f:
                    f.write(plain_text)


                st.markdown(markdown_content)


                st.download_button(
                    "Download Markdown Report",
                    markdown_content,
                    "AI_GenAI_Proposal.md",
                    "text/markdown"
                )
                st.download_button(
                    "Download Plain Text Report",
                    plain_text,
                    "AI_GenAI_Proposal_PlainText.txt",
                    "text/plain"
                )

            except Exception as e:
                st.error(f"Error generating report: {str(e)}")

    elif submitted:
        st.warning("Please enter both company name and industry.")

if __name__ == "__main__":
    main()
