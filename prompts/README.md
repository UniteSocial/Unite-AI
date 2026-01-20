# System Prompts

This directory contains all system prompts used by Unite-I for content analysis.

## Transparency Principle

Per our "Code is Public, Configuration is Private" principle, all prompts that influence
how the AI makes decisions are published here. This allows anyone to:

1. Audit what instructions the AI receives
2. Verify no hidden political bias exists in the prompts
3. Suggest improvements via pull requests
4. Build the same system with identical behavior

## Prompt Files

| File | Purpose |
|------|---------|
| `classification_en.txt` | English content type classification |
| `classification_de.txt` | German content type classification |
| `political_analysis_en.txt` | English political tendency analysis |
| `political_analysis_de.txt` | German political tendency analysis |
| `intent_analysis_en.txt` | English intent detection |
| `intent_analysis_de.txt` | German intent detection |
| `veracity_en.txt` | English fact-checking |
| `veracity_de.txt` | German fact-checking |

## Template Variables

Prompts use the following template variables that are filled at runtime:

- `{text}` - The content being analyzed
- `{labels}` - Available classification labels
- `{claim}` - The claim being fact-checked
- `{current_date}` - Current date for temporal context
- `{search_context}` - Web search results for verification

## Modifying Prompts

Changes to these prompts directly affect analysis behavior. All modifications
should be reviewed carefully and tested before deployment.
