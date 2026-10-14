# Deciding what is blocking, and asking it

## The test

An uncertainty is a **blocking** only if all three hold:

1. **Divergence.** Two or more readings are plausible and they lead to materially different
   outcomes along at least one of: business behavior, data model, public interface, scope,
   security, compatibility, a destructive or irreversible act, the mode itself.
2. **Not settled.** After step 3 neither the conversation nor the project settles it, and no
   decision the person already stated does.
3. **Costly to guess.** A wrong guess is not cheap to undo — the executor would build on it, or
   it would touch something that cannot be restored.

Missing any one makes it not a blocking:

- A reading the project settles, or one the person already decided: use it.
- A reversible detail with one conservative reading: take the reading that changes least,
  preserves existing behavior and is easiest to undo, and list it under ASSUMPTIONS when it
  changes what is executed.
- Anything the executor can look up: write it under DISCOVERY.

Two readings that differ only in wording, or options that differ only in care ("implement
correctly" / "implement carefully"), are not alternatives. Present only options that are
materially different, technically plausible, and relevant to the decision.

## Asking

Each blocking becomes one question of the `AskUserQuestion` call:

- the question names the decision and, in one sentence, why it changes the result;
- 2 to 4 options, each a different outcome, with its consequence in the option's description;
- the recommended option is first and its label ends with `(Recommended)`;
- the header is a short noun for the decision.

Independent blockings go in the same call. A blocking that depends on the answer to another waits
for it and is asked only if it still exists. Two calls at most, in all.

A recommendation is derived, never preferred. Take the first level of this list that separates the
options, and say which in the recommendation:

1. what the person stated, here or earlier;
2. what the project's standards, specifications and decisions state;
3. what the existing implementation and conventions already do;
4. preserving current behavior and compatibility;
5. the change that is smallest, least destructive and easiest to reverse.

A recommendation is not a choice. The person's answer is the decision, and a recommended option
the person did not select is not captured.

Never recommend over the person's own questions: which of two readings of their words they meant,
and whether an irreversible act should happen at all, are theirs: the question offers those
options with no `(Recommended)` label and says, in its own words, that the choice is theirs and
what each option assumes.

## Capturing the answer

Each answer becomes a line of the instruction, stated as the decision with its direct consequence
for the executor and nothing more: a person who selected "preserve the public interface" yields
"Preserve the public interface of <the module>" and no further rule. An answer given as free text
is captured in the person's words.
