## ADDED Requirements

### Requirement: A habit rule rests on measured evidence

Each rule the package adds for a speech habit SHALL record, in its test fixtures' notes, the habit's agent-to-human log ratio and the counts on each side that produced it.

#### Scenario: A new rule shows its numbers

- **WHEN** a change adds a rule for a habit from the frequency research
- **THEN** the rule's test fixtures name the ratio, the agent count and the human count from that research

### Requirement: A habit spreads across sources

A word or phrase SHALL become a rule only when it occurs in at least half of the large agent sources for a single word, 35% for two words, or 25% for three.

#### Scenario: A topic word stays out

- **WHEN** a word ranks high on ratio but occurs in only a few agent repositories
- **THEN** no rule flags it

### Requirement: The package flags no house vocabulary

A word that ranks high only because one organization's guides use it, such as "shall" or "the operator's", SHALL NOT become a rule.

#### Scenario: A guide term stays out

- **WHEN** a word's high ratio comes from requirement language or a team's own terms
- **THEN** no rule flags it
