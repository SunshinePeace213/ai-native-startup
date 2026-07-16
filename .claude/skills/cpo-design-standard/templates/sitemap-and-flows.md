# Sitemap & Flows — <Client Name>

Source: prd.md (structure & pages). Every page here has a matching entry in
section-briefs.md and a wireframe under design/wireframes/.

## Sitemap

```mermaid
graph TD
  Home[Home]
  Home --> About[About]
  Home --> Features[Features / Services]
  Home --> Pricing[Pricing]
  Home --> Contact[Contact]
  Home --> Legal[Privacy & Terms]
```

## Primary user flow

The path from landing to the primary desired action.

```mermaid
flowchart LR
  Land[Land on Home] --> Scan[Scan hero + proof]
  Scan --> Explore[Explore features]
  Explore --> Act[Primary action: <e.g. submit contact form>]
  Act --> Confirm[Confirmation / next step]
```

## Notes

- <Secondary flows, conditional paths, or navigation rules the designer should know.>
