"""JSON-LD schema markup generator for GEO optimization."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.utils.logger import logger


class SchemaGenerator:
    """Generate JSON-LD schema markup for various content types."""

    def __init__(self):
        """Initialize schema generator."""
        pass

    def generate_article_schema(
        self,
        title: str,
        description: str,
        url: str,
        author_name: str,
        author_url: Optional[str] = None,
        publish_date: Optional[str] = None,
        modified_date: Optional[str] = None,
        image_url: Optional[str] = None,
        organization_name: Optional[str] = None,
        organization_url: Optional[str] = None,
    ) -> str:
        """
        Generate Article schema markup.

        Args:
            title: Article title
            description: Article description
            url: Article URL
            author_name: Author name
            author_url: Optional author URL
            publish_date: Optional publish date (ISO format)
            modified_date: Optional modified date (ISO format)
            image_url: Optional featured image URL
            organization_name: Optional organization name
            organization_url: Optional organization URL

        Returns:
            JSON-LD schema markup as HTML script tag
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": description,
            "url": url,
        }

        # Author
        author = {"@type": "Person", "name": author_name}
        if author_url:
            author["url"] = author_url
        schema["author"] = author

        # Publisher (Organization)
        if organization_name:
            publisher = {"@type": "Organization", "name": organization_name}
            if organization_url:
                publisher["url"] = organization_url
            schema["publisher"] = publisher

        # Dates
        if publish_date:
            schema["datePublished"] = publish_date
        else:
            schema["datePublished"] = datetime.now().isoformat()

        if modified_date:
            schema["dateModified"] = modified_date
        else:
            schema["dateModified"] = datetime.now().isoformat()

        # Image
        if image_url:
            schema["image"] = {
                "@type": "ImageObject",
                "url": image_url,
            }

        return self._format_schema(schema)

    def generate_organization_schema(
        self,
        name: str,
        url: str,
        logo_url: Optional[str] = None,
        description: Optional[str] = None,
        contact_point: Optional[Dict[str, Any]] = None,
        social_links: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate Organization schema markup.

        Args:
            name: Organization name
            url: Organization URL
            logo_url: Optional logo URL
            description: Optional organization description
            contact_point: Optional contact point dict with "telephone", "email", "contactType"
            social_links: Optional dict with social media links (e.g., {"facebook": "...", "twitter": "..."})

        Returns:
            JSON-LD schema markup as HTML script tag
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": name,
            "url": url,
        }

        if logo_url:
            schema["logo"] = logo_url

        if description:
            schema["description"] = description

        # Contact point
        if contact_point:
            schema["contactPoint"] = {
                "@type": "ContactPoint",
                "contactType": contact_point.get("contactType", "Customer Service"),
            }
            if contact_point.get("telephone"):
                schema["contactPoint"]["telephone"] = contact_point["telephone"]
            if contact_point.get("email"):
                schema["contactPoint"]["email"] = contact_point["email"]

        # Social media links
        if social_links:
            same_as = []
            for platform, link in social_links.items():
                same_as.append(link)
            if same_as:
                schema["sameAs"] = same_as

        return self._format_schema(schema)

    def generate_faq_schema(self, faqs: List[Dict[str, str]]) -> str:
        """
        Generate FAQPage schema markup.

        Args:
            faqs: List of FAQ dictionaries with "question" and "answer" keys

        Returns:
            JSON-LD schema markup as HTML script tag
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [],
        }

        for faq in faqs:
            if "question" in faq and "answer" in faq:
                schema["mainEntity"].append({
                    "@type": "Question",
                    "name": faq["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq["answer"],
                    },
                })

        return self._format_schema(schema)

    def generate_person_schema(
        self,
        name: str,
        job_title: Optional[str] = None,
        organization_name: Optional[str] = None,
        organization_url: Optional[str] = None,
        url: Optional[str] = None,
        image_url: Optional[str] = None,
        description: Optional[str] = None,
        social_links: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate Person schema markup (for author).

        Args:
            name: Person name
            job_title: Optional job title
            organization_name: Optional organization name
            organization_url: Optional organization URL
            url: Optional personal URL
            image_url: Optional profile image URL
            description: Optional description
            social_links: Optional dict with social media links

        Returns:
            JSON-LD schema markup as HTML script tag
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": name,
        }

        if job_title:
            schema["jobTitle"] = job_title

        if organization_name:
            affiliation = {"@type": "Organization", "name": organization_name}
            if organization_url:
                affiliation["url"] = organization_url
            schema["affiliation"] = affiliation

        if url:
            schema["url"] = url

        if image_url:
            schema["image"] = image_url

        if description:
            schema["description"] = description

        # Social media links
        if social_links:
            same_as = []
            for platform, link in social_links.items():
                same_as.append(link)
            if same_as:
                schema["sameAs"] = same_as

        return self._format_schema(schema)

    def generate_breadcrumb_schema(self, items: List[Dict[str, str]]) -> str:
        """
        Generate BreadcrumbList schema markup.

        Args:
            items: List of breadcrumb items with "name" and "url" keys

        Returns:
            JSON-LD schema markup as HTML script tag
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [],
        }

        for i, item in enumerate(items):
            if "name" in item and "url" in item:
                schema["itemListElement"].append({
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": item["name"],
                    "item": item["url"],
                })

        return self._format_schema(schema)

    def generate_combined_schema(
        self,
        article_data: Dict[str, Any],
        organization_data: Optional[Dict[str, Any]] = None,
        person_data: Optional[Dict[str, Any]] = None,
        faq_data: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Generate combined schema markup for multiple types.

        Args:
            article_data: Article schema data
            organization_data: Optional organization schema data
            person_data: Optional person schema data
            faq_data: Optional FAQ data

        Returns:
            Combined JSON-LD schema markup as HTML script tags
        """
        schemas = []

        # Generate Article schema
        if article_data:
            article_schema = self.generate_article_schema(**article_data)
            schemas.append(article_schema)

        # Generate Organization schema
        if organization_data:
            org_schema = self.generate_organization_schema(**organization_data)
            schemas.append(org_schema)

        # Generate Person schema
        if person_data:
            person_schema = self.generate_person_schema(**person_data)
            schemas.append(person_schema)

        # Generate FAQ schema
        if faq_data:
            faq_schema = self.generate_faq_schema(faq_data)
            schemas.append(faq_schema)

        return "\n\n".join(schemas)

    def _format_schema(self, schema: Dict[str, Any]) -> str:
        """
        Format schema dictionary as HTML script tag.

        Args:
            schema: Schema dictionary

        Returns:
            HTML script tag with JSON-LD schema
        """
        json_str = json.dumps(schema, indent=2, ensure_ascii=False)
        return f'<script type="application/ld+json">\n{json_str}\n</script>'

    def validate_schema(self, schema_json: str) -> tuple[bool, Optional[str]]:
        """
        Validate JSON-LD schema format.

        Args:
            schema_json: JSON-LD schema as string

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Remove script tags if present
            schema_text = schema_json.strip()
            if schema_text.startswith("<script"):
                # Extract JSON from script tag
                json_match = schema_text.split(">", 1)[1].rsplit("</script>", 1)[0]
                schema_text = json_match.strip()

            schema = json.loads(schema_text)

            # Basic validation
            if "@context" not in schema:
                return False, "Missing @context field"

            if "@type" not in schema:
                return False, "Missing @type field"

            # Validate context is schema.org
            context = schema.get("@context")
            if isinstance(context, str) and "schema.org" not in context:
                return False, "@context should reference schema.org"

            return True, None

        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"

        except Exception as e:
            return False, f"Validation error: {str(e)}"

