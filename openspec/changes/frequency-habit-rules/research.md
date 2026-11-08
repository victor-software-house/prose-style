# Research: habits by frequency

This change asks which words, phrases and punctuation habits agent-written technical prose uses far more often than human technical prose from before 2022.  
The answer comes from counts on two cleaned corpora, a ratio per n-gram, and a linear model that separates the two.  
Data was collected and measured on 2026-11-08 (UTC).

## Corpora

The agent side holds text written by coding agents in 2025 and 2026, of three kinds.

| Kind | Source | Sentences | Words |
|:--|:--|--:|--:|
| Docs | Markdown files agents added to the organization's repositories since 2025-06-01 | 151,783 | 2,531,868 |
| Replies | Agent replies in 176 coding sessions from the last 30 days | 170,457 | — |
| Thinking | Agent reasoning blocks in the same sessions | 288,476 | — |

Docs leave out changelogs, licenses, vendored or generated folders, test fixtures and archives.  
Session text leaves out tool calls, tool results, sub-agent turns, compaction summaries and harness messages, and each block counts once across resumed sessions.

The human side holds text written before ChatGPT's release on 2022-11-30.

| Source | Pin | Sentences |
|:--|:--|--:|
| [Rust RFCs][rfcs] | [16f3bc0][rfcs-pin] | 126,546 in all four design-doc sets |
| [Python PEPs][peps] | [f2f542d][peps-pin] | |
| [Go proposals][go-proposal] | [983df79][go-pin] | |
| [Kubernetes enhancements][k8s] | [5c1ad04][k8s-pin] | |
| [Stack Exchange data dump][se-dump], April 2024, posts before 2022-11-30 | 8 sites below | 2,940,693 |

Each design-doc pin is the last commit before 2021-12-31.  
The Stack Exchange sites, with sentences kept:

| Site | Sentences |
|:--|--:|
| codereview | 566,312 |
| softwareengineering | 454,476 |
| stats | 453,779 |
| mathoverflow | 385,435 |
| cs | 375,876 |
| unix | 297,497 |
| math | 253,796 |
| cstheory | 153,522 |

Each site gave up to 60,000 questions and answers with a score of 2 or more, sampled evenly by post id.  
cstheory had 22,794 such posts and cs 50,420.

## Cleaning

Every corpus goes through the same steps, so a difference cannot come from parsing.

1. Parse each format with its own parser: [markdown-it-py][markdown-it] 4.0.0 for Markdown, [docutils][docutils] 0.21.2 for reStructuredText, and Python's `html.parser` for Stack Exchange HTML.  
   Only paragraphs and list items remain; code, tables, block quotes, headings and HTML blocks are dropped.
2. Replace inline code, math and URLs with one placeholder, so no n-gram spans removed text.
3. Split sentences, then keep a sentence only when it has 5 to 60 words, starts with a capital or a quote, and holds no more than one stray symbol.  
   At least 85% of its tokens must look like words, and at least 70% of its words must be common English: a [wordfreq][wordfreq] 3.1.1 Zipf score of 3 or more.
4. Drop exact duplicates, compared case-folded.

Agent docs lost 26,690 duplicates and 52,838 sentences outside the length range; the other filters removed 58,554 more.

## Method

Each n-gram of one to three words gets the log ratio from the [lexa-index][lexa] project:  
lpr = log2(((cM + 0.5) / (NM + 1)) / ((cH + 0.5) / (NH + 1))),  
where cM and cH count the n-gram on each side, and NM and NH count all n-grams there.

Two filters keep habits apart from topics.

- An n-gram needs at least 20 agent uses.
- It must occur in many agent sources: half of the large repositories for a single word, 35% for two words, 25% for three.  
  A source counts as large at 500 sentences or more.

[spaCy][spacy] 3.8.7 with `en_core_web_sm` 3.8.0 tags each word's most common part of speech, so verbs, adjectives and adverbs can be read apart from nouns.

A logistic regression then tests whether the habits separate the two sides at all.  
Nouns, proper nouns and numbers become their tags, so topic words carry no signal.  
Each source gets an even share of 60,012 sentences per side, and the five folds split by source, so a test fold never shares a repository or site with training.

## Results

### Punctuation and constructions

Rates per 1,000 words:

| Measure | Agent docs | Agent replies | Agent thinking | Design docs | SE softeng | SE unix | SE cs | SE math | SE mathoverflow |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Em dash | 2.18 | 0.01 | 2.97 | 0.06 | 0.06 | 0.18 | 0.10 | 0.06 | 0.06 |
| Semicolon | 8.05 | 2.24 | 0.32 | 1.10 | 0.83 | 0.96 | 1.16 | 1.09 | 1.20 |
| Colon inside a sentence | 9.47 | 11.96 | 4.29 | 2.39 | 1.84 | 1.94 | 2.69 | 2.94 | 3.27 |
| ", not the" and its kin | 0.69 | 0.34 | 0.14 | 0.09 | 0.11 | 0.12 | 0.07 | 0.07 | 0.06 |
| "not X but Y" | 0.02 | 0.01 | 0.02 | 0.17 | 0.30 | 0.23 | 0.22 | 0.20 | 0.27 |
| Three-item list | 3.21 | 1.74 | 1.28 | 0.74 | 0.93 | 0.46 | 0.48 | 0.33 | 0.48 |
| "so the", "so it" | 1.54 | 2.67 | 2.16 | 0.22 | 0.16 | 0.25 | 0.30 | 0.38 | 0.27 |
| "we" | 0.32 | 0.19 | 0.07 | 5.22 | 2.46 | 1.03 | 7.37 | 9.09 | 4.66 |
| Question mark | 0.48 | 0.23 | 0.03 | 0.72 | 4.56 | 5.39 | 4.60 | 5.51 | 4.07 |
| Arrow | 0.40 | 0.06 | 0.03 | 0 | 0 | 0.01 | 0.01 | 0 | 0.02 |

Agent docs use semicolons seven times as often as design docs, and colons inside a sentence four times as often.  
Agents write ", not the" contrasts seven times as often, and almost never the human "not X but Y".  
Humans write "we" and ask questions far more.  
Agent replies average 13.4 words per sentence with a standard deviation of 5.8; in human text the deviation runs from 9 to 11.

### Words and phrases in agent docs

The spread filter kept 1,724 single words, 2,041 pairs and 453 triples, across 58 large agent sources and 12 human ones.  
The verbs, adjectives and adverbs with the highest ratios fall into two groups.

- Verbs that make a thing act: owns (6.07), refuses (6.06), survives (5.53), stays (5.33), carries (5.18), waits (5.16), keeps (4.87), also emits, restores, resolves, skips, supplies, declares, exposes, resumes and replaces.
- Stock adjectives and adverbs: durable (8.52), pinned, stale, gated, scoped, authoritative, deliberate, silently, verbatim, untouched, observable.

Phrases: "byte identical" (127 agent uses against 2 human), "byte for byte" (130 against 15), "source of truth" (249 against 36), "keeps its own" (57 against 3), "not silently" (98 against 7).

Some leaders belong to our own repositories, such as "the operator's", "shall" and tool names; a rule must leave them out.  
Agent replies rank status-report words first ("rebased", "queued", "landed", "once CI is green"), which fit a review of chat more than a docs lint.

Eleven of these words also appear in the [claudeisms][claudeisms] list (surfaces, carries, stays, survives, renders, lands, wiring, handoff, drift, ships, touches).  
Lists built for fiction or papers fit worse: 12 of 1,648 [slop-score][slop-score] words and 52 of 407 academic style words from [Kobak et al.][excess-vocab] pass the spread filter.

### The linear model

Held-out ROC AUC per fold, with topic words masked:

| Fold | AUC | Sentences |
|:--|--:|--:|
| 0 | 0.958 | 15,832 |
| 1 | 0.985 | 21,568 |
| 2 | 0.987 | 30,484 |
| 3 | 0.981 | 29,414 |
| 4 | 0.970 | 22,726 |

So the habits alone separate the two sides on repositories and sites the model never saw.  
Agent-side features include the em dash (2,803 agent sentences against 84 human), the semicolon (6,842 against 1,005), "→", ", not", "stays", "owns", "keeps", "stale", "durable" and "verbatim".  
Human-side features include "I", "however", "thus", "hence", "i.e.", "suppose", "note that", "perhaps" and "seems".  
Agent-side features also hold genre markers from our guides, such as "good, because" (398 against 0) and "shall", so the model learns genre as well as voice.

## Limits

- The agent docs come from one organization's repositories, written under one set of guides; another team's agents may lean differently.
- Design docs and Stack Exchange answers differ in genre from agent guides and specs, and that difference inflates words such as "shall" and "do not".
- The human sources run to 2021 and 2022; usage has moved since, apart from any model.
- wordfreq's Zipf filter favors common words, so rare technical terms cannot reach a rule this way.

## Candidates

Each candidate below scored high on both sides of the evidence: a large ratio and a wide spread.

1. Semicolons and colons inside a sentence, as warnings above a rate per paragraph.
2. ", not the" contrasts, beside the existing rule for "not X but Y".
3. Three-item lists, at a rate per paragraph.
4. "so the" and "so it" opening a clause.
5. Verbs that make things act: owns, refuses, survives, carries, stays, waits, keeps, sits, lives.
6. Stock adjectives and adverbs: durable, authoritative, deliberate, silently, verbatim.
7. Phrases: "byte identical", "byte for byte", "source of truth", "keeps its own".

The em dash already has a rule.

[rfcs]: https://github.com/rust-lang/rfcs
[rfcs-pin]: https://github.com/rust-lang/rfcs/tree/16f3bc024bdef9db7502ffbefeb602c37cee20bf
[peps]: https://github.com/python/peps
[peps-pin]: https://github.com/python/peps/tree/f2f542d54442d7304b95ff6652ec89b6e6a2d45b
[go-proposal]: https://github.com/golang/proposal
[go-pin]: https://github.com/golang/proposal/tree/983df7993af0dda308e4efa51b0e451fbe09aa17
[k8s]: https://github.com/kubernetes/enhancements
[k8s-pin]: https://github.com/kubernetes/enhancements/tree/5c1ad04863bc65ecb72abc3b9dc0064695be90b8
[se-dump]: https://archive.org/details/stackexchange
[markdown-it]: https://github.com/executablebooks/markdown-it-py
[docutils]: https://docutils.sourceforge.io/
[wordfreq]: https://github.com/rspeer/wordfreq
[lexa]: https://github.com/fsu-nlp/lexa-index/tree/f74efecdf0002956ce04c3d1a7b529929f9b0966
[spacy]: https://spacy.io/
[claudeisms]: https://github.com/archiewood/claudeisms/tree/49f625b657edcdba8e43fb2857975d9d50c72d96
[slop-score]: https://github.com/sam-paech/slop-score/tree/289264ab2a0df1358ef81ced3c259610ea709514
[excess-vocab]: https://github.com/berenslab/llm-excess-vocab/tree/53db991afc251782106cd817a1c3fa47a4d41781
