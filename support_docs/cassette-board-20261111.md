# Cassette board: cards, order and worker (2026-11-11)

This file is the complete card set for the six remaining stages, and the standing instructions for the
worker that goes through them. It was written from the pushed repository, the Linear board, and the
transcripts of the four Cassette sessions of 11 November.

## A. What to do with this file (for the agent on the Mac)

1. In Linear (team Reclusestudio, label `cassette`): create one card per entry in section D, as a
   sub-issue of the stage card named in its heading. State Backlog, priority High, title exactly as given.
   Create the rules card in section B first and put its identifier where the cards say REC-RULES.
2. Cancel REC-374, REC-375, REC-376, REC-377 and REC-378. They are the five-stage cards and are replaced
   by the six stage cards REC-407 to REC-412. Copy the three measurement comments on REC-374 into card 05.08.
3. Make REC-396 a sub-issue of REC-411 and rename it `Cassette 09.08 — Compare measured speed with the maths`.
4. Register the scheduled task in section C on the Mac and run it once.
5. Ask Drew nothing. Report in three lines when it is done.

## B. Rules card

Title: `Cassette 00 — Working rules for every Cassette card (read first, never close)`. State Backlog.

**The plan.** Six stages remain, L05 to L10. Each has one test in `tests/test_live_stage_acceptance.py`.
A stage is done when its one test passes. The numbered cards are the steps that get a stage to its test.

**Where.** The Mac, in `/Volumes/LaCie/drewwiberg-lacie/cassette`. `~/cassette` is stale; do not use it.
Read `AGENTS.md` and the newest entries in `FIRST_PRINCIPLES.md` first. Evidence and logs for a card go in
`/Volumes/LaCie/drewwiberg-lacie/codex-runtime/cassette-board/<card number>/`.

**Rules.**

1. One branch. Work on `main` in that checkout. No per-card branch, no worktree. Commit messages answer
   the three questions `AGENTS.md` requires. Push `main` to `origin` when a card is done.
2. Whole model, exact answers. No shrunken or lossy copy presented as the model. After any speed change
   the output text must match the earlier output exactly.
3. The equipment is settled: Drew's MacBook Air (M4, 24 GB), the LaCie 5 TB hard disk, and Ollama as the
   download source and the client. Never propose other hardware.
4. Long jobs. Start downloads and long runs detached, with a log and a state file in the card's evidence
   folder. Put the exact resume command in the end comment and leave the card In Progress. On resume,
   check the job first. Never start a second copy of a running job.
5. Do not ask Drew routine questions and never hand him a button to press. Decide, write the decision and
   the reason in `FIRST_PRINCIPLES.md`, continue.
6. Only these go to Drew: a password, a licence acceptance, a payment, or a physical action such as
   unplugging the drive. Do everything else first, write a spec in `support_docs/`, set the card to
   In Review, and move on to the next card that does not need it.
7. Honest results. Record every result with its numbers in `FIRST_PRINCIPLES.md`. A failed check is
   recorded as failed.
8. Shared drive. Other work uses the LaCie. Touch only Cassette's files.
9. No extra reviews. No second-agent review and no approval step closes a card. Only its "Done when" does.
10. Plain speech in comments and the worklog. Short everyday words. No stage codes without a plain name.

## C. The worker (scheduled task on the Mac)

Name `cassette-board-worker`. Every hour, all day and night (`30 * * * *`). Working folder
`/Volumes/LaCie/drewwiberg-lacie/cassette`. Set it to run without permission prompts. Prompt:

```text
You work the Cassette cards on the Linear board (team Reclusestudio, label "cassette") until all are done.
Read the rules card "Cassette 00 — Working rules for every Cassette card" and follow it. One card per run.

1. Resume first. List cassette cards that are In Progress and have a number in the title (05.01 and so on).
   Read the newest comment on each.
   - Newest comment starts "Cassette run started" and is under 90 minutes old: another run is working.
     Stop and say so in one line.
   - Otherwise that card was interrupted or is waiting on a long job. Resume it. Check for its running job
     before anything else, using the resume notes in its last comment and its evidence folder.
2. Otherwise pick. Take the lowest-numbered card that is not Done, Canceled or In Review and whose
   "Needs" cards are all Done. If a needed card is In Review, skip to the next card that does not need it.
   If nothing can be picked, stop and say which card is waiting on Drew.
3. Claim. Set the card In Progress. Comment "Cassette run started <ISO time>" with two plain sentences on
   what you will do.
4. Do the card to its "Done when". Follow the rules card.
5. Close out. Comment "Cassette run ended <ISO time>": what was done, the numbers, where the evidence is,
   what remains, and the exact way to resume. Then set Done, In Review (with the support_docs spec named),
   or leave In Progress if work remains.
6. When the last card of a stage is Done and the stage's one test has passed, set the stage card Done and
   the next stage card In Progress.
7. When every numbered card and all six stage cards are Done, disable this scheduled task and say so.
```

## D. Cards

Every card's description starts with: `Read REC-RULES first.` Then Goal, Steps, Done when, Needs.

### Stage L05, check the drive and download the models (parent REC-407, test `test_l05_complete`)

**Cassette 05.01 — Save today's work and leave the checkout clean.** Needs: nothing.
Goal: nothing from 11 November is lost and the code is in a known, committed state.
Steps: run `git status`. Uncommitted edits to `pager.py`, `store.py`, `broker.py`, `compiler.py` and
`tests/test_l02_native.py` are the exact speed changes from the 11 November speed session, which was
interrupted while taking them out. Copy those five files to the evidence folder. Save the diff as
`support_docs/exact-speed-changes-20261111.patch`. Restore the five files to the last commit, then check
the patch still applies with `git apply --check`. Commit the patch, `support_docs/` and the worklog.
Run the store, pager, broker and model tests. Push `main` (this also publishes `eab79bc`, `be4343f`, `9c26cb3`).
Done when: `git status` is clean, `origin/main` equals local `main`, the patch file exists and applies.

**Cassette 05.02 — Make the written plan say what Drew decided.** Needs: 05.01.
Goal: the files stop contradicting Drew. Today `AGENTS.md`, `IMPLEMENTATION.md` and `FIRST_PRINCIPLES.md`
say five stages; Drew's instruction is six stages, L05 to L10, one test each.
Steps: in those three files and `PHASE_LIVE_RUNBOOK.md`: (1) state six stages, one test each, with the
stage text from the October queue (branch `origin/codex/prepared-source-consumer`, `IMPLEMENTATION.md`
records L05 to L10), minus any reviewer condition; (2) name the equipment: the M4 Air, the LaCie hard
disk, Ollama as tested source and client, with Hugging Face used where a model is not on Ollama;
(3) remove "principal present" and every review or approval gate; put anything needing Drew's hands in
L10; (4) record that Tinker, Codex, OpenClaw and Hermes rows are not tested in this run and say so
plainly in the results. Change no threshold. Regenerate generated files with their generator.
Done when: the four files agree, the schema test passes, and the worklog records each change.

**Cassette 05.03 — Move Cassette's files out of the disk image into a folder on the LaCie.** Needs: 05.02.
Goal: faster reads and saves, and room for the downloads. Measured 11 November: reads 20 to 25 MB/s in
the image against 73 to 89 directly; a safe save 1.44 s against 0.20 s. The image also stops at 2 TB and
the downloads need 2.3 TB.
Steps: create `/Volumes/LaCie/drewwiberg-lacie/cassette-cartridge/Cartridge/`. Select it with the
existing drive commands. Copy the prepared Qwen3-4B there and verify every file by its fingerprint. Ask
it the France question and compare the text with the morning baseline. Leave the image file untouched.
Record in the worklog that proving a remount now needs a real unplug, which is in card 10.03.
Done when: Qwen3-4B answers from the folder with identical text and the read and save rates are measured.

**Cassette 05.04 — Space download saves further apart.** Needs: 05.03.
Goal: downloads limited by the network. Today a safe save every 4 MB holds them to 2.9 MB/s.
Steps: change the save spacing to 256 MB in the download rule (Q51) and in the source-profile checker
together, since the checker recomputes the save order and rejected an earlier attempt. Keep the final
fingerprint check on every file. Test: download a model of 1 GB or more, interrupt it, resume it.
Done when: the download resumes correctly after the interrupt, every file verifies, and the measured
rate is recorded beside the old 2.9 MB/s.

**Cassette 05.05 — Make a model downloaded from Ollama prepare and answer.** Needs: 05.03.
Goal: Ollama works as the source end to end. On 11 November `smollm:135m` downloaded from Ollama in 55 s
and then failed at the prepare step. Nobody looked into why.
Steps: reproduce with `smollm:135m`. Find the cause. Fix it in the existing prepare path. Ask the
prepared model a question through the real Ollama app pointed at Cassette.
Done when: a model downloaded from Ollama answers through the Ollama app, with the cause and fix recorded.

**Cassette 05.06 — List every required download and check the space.** Needs: 05.02.
Goal: one table of what stage L05 needs on the drive and where each item stands.
Steps: read `test_l05_complete` and the frozen input records (the twenty selections, 2,317,278,417,259
bytes, under `~/.codex/reviews/cassette/2026-10-26/l05-resume-01`). Write
`support_docs/l05-downloads.md`: item, source, pinned revision, bytes, on the drive or not. Check free
space on the LaCie against the total plus working room.
Done when: the table is committed. If space is short, say by how much and set In Review.

**Cassette 05.07 — Run the full drive measurement.** Needs: 05.03.
Goal: the stage's drive measurement, on the folder location, with a recorded result.
Steps: run the product's drive check with its full sweep: six read sizes, three patterns, four queue
depths, cold and warm, safe writes, then one hour sustained. Run it detached. Compare with the plan's
bounds for the jobs that follow.
Done when: the result file exists and each bound is recorded as met or not met.

**Cassette 05.08 — Download Qwen3-30B-A3B (61 GB).** Needs: 05.04, 05.06.
Steps: download `Qwen/Qwen3-30B-A3B` at revision `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39` to the
folder with the product commands, detached. Verify every file.
Done when: all 61,084,187,391 bytes are on the drive and verified, with the rate recorded.

**Cassette 05.09 — Bring Qwen3-30B in through Ollama's format.** Needs: 05.05, 05.08.
Goal: the plan's Ollama re-import: the same model, offered in Ollama's layout from the verified bytes
on the drive, imported again, with its identity unchanged.
Done when: the re-imported model's identity equals the original's and the receipt is saved.

**Cassette 05.10 — Download the question sets and the comparison models.** Needs: 05.04, 05.06.
Steps: download every dataset and every "what the Air can run by itself" candidate model in the table
from 05.06. Verify each.
Done when: every such row in the table reads "on the drive, verified".

**Cassette 05.11 — Download Qwen3-235B (470 GB).** Needs: 05.08.
Steps: `Qwen/Qwen3-235B-A22B-Instruct-2507` at `ac9c66cc9b46af7306746a9250f23d47083d689e`, detached.
Done when: all files are on the drive and verified.

**Cassette 05.12 — Download Kimi K3 (1.56 TB).** Needs: 05.11.
Steps: `moonshotai/Kimi-K3` at `9f62e4e9fffbd0a83ddd60e1c209d828994b3569`, detached. This runs for days.
Done when: all 96 weight files are on the drive and verified.

**Cassette 05.13 — Run the L05 test and close the stage.** Needs: 05.07, 05.09, 05.10, 05.12.
Steps: run `tests/test_live_stage_acceptance.py::test_l05_complete`. Fix what fails, within the plan.
Done when: that one test passes. Then set REC-407 Done.

### Stage L06, measure the comparisons (parent REC-408, test `test_l06_complete`)

**Cassette 06.01 — Write the one test for stage L06.** Needs: 05.13.
Steps: add `test_l06_complete` to the stage test file from the plan's "done when" for L06 and the
matrix. It must fail today for the right reason.
Done when: the test exists, fails only on work not yet done, and is committed.

**Cassette 06.02 — Stop Cassette pushing the Mac into swap.** Needs: 05.13.
Goal: the memory check counts what else is running. Today it reports zero for other programs and grants
itself 17 GB; runs at 12 GB grew swap, runs at 10 GB or less did not.
Done when: a run that used to grow swap is either admitted at a size that leaves swap flat or refused,
and the measurement is recorded.

**Cassette 06.03 — Put back the saved exact speed changes, one at a time.** Needs: 06.02.
Goal: answers fast enough to measure with. Morning baseline 5,958 s for 64 words; with the changes 360 s.
Steps: from `support_docs/exact-speed-changes-20261111.patch` and
`support_docs/packed-residency-20261111.patch`, apply one change at a time. After each: tests, then the
same 64-word question; the text must match the baseline exactly. Drop any change that does not.
Done when: each change is committed separately with its before and after time, or recorded as dropped.

**Cassette 06.04 — Measure what the Air can run by itself.** Needs: 06.01, 05.10.
Steps: run each candidate model in plain Ollama on the Air, no Cassette, on the frozen question set.
Record quality and speed. Pick the strongest from the measurements only.
Done when: the winner and every candidate's numbers are recorded.

**Cassette 06.05 — Capture each model's own reference answers.** Needs: 06.03, 06.04.
Steps: Qwen3-4B and Qwen3-30B: run the whole exact model from the drive on the question set. Qwen3-235B
and Kimi K3: use the same model through Drew's existing Ollama login if it is offered there. If it is
not, write the spec and set In Review for that model only.
Done when: each model has reference answers saved, or a spec naming exactly what is missing.

**Cassette 06.06 — Run the L06 test and close the stage.** Needs: 06.05.
Done when: `test_l06_complete` passes. Then set REC-408 Done.

### Stage L07, prove the mid-size method on Qwen3-4B (parent REC-409, test `test_l07_complete`)

**Cassette 07.01 — Write the one test for stage L07.** Needs: 06.06.
Done when: `test_l07_complete` exists, fails only on work not yet done, and is committed.

**Cassette 07.02 — Record how Qwen3-4B behaves on the frozen questions.** Needs: 07.01.
Steps: run the existing capture on Qwen3-4B for the frozen question set. Record time and bytes written.
Done when: the capture is on the drive and verified.

**Cassette 07.03 — Run the existing prepare-for-big-models step on Qwen3-4B.** Needs: 07.02.
Steps: run a small bounded part first and work out the time and space the whole job needs. On the 160M
model it took 134 s per block with 6,144,000 blocks. If the whole job on Qwen3-4B needs more than seven
days, record the numbers and fix the single slowest fault, then measure again. No rebuild.
Done when: the step finishes on Qwen3-4B, or the worklog holds the measured reason it cannot.

**Cassette 07.04 — Answer with the prepared model and check the two numbers.** Needs: 07.03.
The two numbers the plan sets: no more than a quarter of the model's bytes touched per word, and answer
quality at least 95% of the reference in every group of questions.
Done when: both numbers are measured and recorded as met or not met.

**Cassette 07.05 — Train Qwen3-4B on the drive.** Needs: 07.02.
Steps: run both kinds of training the plan names, on the drive, with nothing model-sized on the Mac's
own disk. Check the trained model loads, answers, and answers differently.
Done when: both runs finish and the time, memory and bytes written are recorded.

**Cassette 07.06 — Run the L07 test and close the stage.** Needs: 07.04, 07.05.
Done when: `test_l07_complete` passes; set REC-409 Done. If it fails on the two numbers, record the
failure, write `support_docs/l07-result.md` with the numbers, and set In Review. The plan says a failure
here blocks L08, so this is a decision only Drew can make.

### Stage L08, prove the large method on Qwen3-30B (parent REC-410, test `test_l08_complete`)

**Cassette 08.01 — Write the one test for stage L08.** Needs: 07.06.

**Cassette 08.02 — Run Qwen3-30B from the drive and count which sections it uses.** Needs: 08.01.
Goal: the first model built from specialist sections, and the one measurement the theory is waiting on:
how unevenly the sections are used.
Steps: ask the frozen questions. Record seconds per word, bytes read per word, and how often each
section is used.
Done when: the model answers from the drive and the usage table is saved.

**Cassette 08.03 — Prepare Qwen3-30B for big-model answering and answer with it.** Needs: 08.02.
Done when: the plan's numbers for this model are measured and recorded as met or not met.

**Cassette 08.04 — Train Qwen3-30B on the drive.** Needs: 08.02.
Done when: both kinds of training finish, or the measured reason they cannot is recorded.

**Cassette 08.05 — Predict cost against quality for the largest models.** Needs: 08.03.
Steps: fit the curves the plan names from the L07 and L08 measurements and state the predicted point
for Kimi K3 on the Air before running it.
Done when: the prediction is written down with its inputs.

**Cassette 08.06 — Run the L08 test and close the stage.** Needs: 08.03, 08.04, 08.05.
Done when: `test_l08_complete` passes; set REC-410 Done. On failure: same handling as 07.06.

### Stage L09, running, training, the client and failures (parent REC-411, test `test_l09_complete`)

**Cassette 09.01 — Write the one test for stage L09.** Needs: 08.06.

**Cassette 09.02 — Hold full conversations through the real Ollama app.** Needs: 09.01.
Steps: the plan's capability set: plain questions cold and warm, reasoning, code that is then run,
tool calls, structured output, several turns, long context, cancel and recover.
Done when: each item is recorded as passed or failed with the transcript saved.

**Cassette 09.03 — Run for two hours without stopping.** Needs: 09.02.
Done when: 120 minutes and 20,000 generated words are reached, with speed, memory, swap and heat logged.

**Cassette 09.04 — Run each required model on the Air.** Needs: 09.02.
Steps: Qwen3-235B and Kimi K3 from the drive, each on the frozen questions, with the 08.05 prediction
beside the measured result.
Done when: every required model row has a measured result.

**Cassette 09.05 — Run the required training jobs.** Needs: 09.04.
Done when: every training row in the plan has a measured result.

**Cassette 09.06 — Break things on purpose, in software.** Needs: 09.02.
Steps: every failure in the plan that needs no hands: kill mid-download, kill mid-answer, kill mid-save,
damage a stored piece, fill the space, change the source. Each must recover or stop with the right error.
Done when: each failure is recorded as handled or not. Hands-on failures go to 10.03.

**Cassette 09.07 — Prove it works with no network and sends nothing out.** Needs: 09.02.
Done when: a full conversation completes with the network blocked for Cassette, and a capture shows no
outbound traffic.

**Cassette 09.08 — Compare measured speed with the maths.** This is REC-396. Needs: 09.04.
Steps: set each measured number beside what `MATHS.md` and
`support_docs/conversational-speed-first-principles.md` predict. Say where they agree and where not.

**Cassette 09.09 — Run the L09 test and close the stage.** Needs: 09.03, 09.05, 09.06, 09.07, 09.08.
Done when: `test_l09_complete` passes; set REC-411 Done.

### Stage L10, hands-on checks, clean replay and release (parent REC-412, test `test_l10_complete`)

**Cassette 10.01 — Write the one test for stage L10.** Needs: 09.09.

**Cassette 10.02 — Get the code-accounting checks passing.** Needs: 10.01.
Steps: regenerate the accounting report with its own tool; fix `test_s26_machine_gate` and `test_s27`.
Done when: the full test suite and the ledger pass.

**Cassette 10.03 — One hands-on session for Drew, prepared in full.** Needs: 10.02.
Goal: everything that needs Drew's hands, once. Unplug and replug during a save, during a download and
during an answer, plus anything earlier cards parked.
Steps: write `support_docs/hands-on-session.md`: each action in order, what to watch for, how long.
Start the watcher that records the results. Set In Review.
Done when: Drew has done the session and every action is recorded as passed or failed.

**Cassette 10.04 — Repeat everything from a clean start.** Needs: 10.03.
Steps: fresh checkout, empty Cassette folder, run every stage's work again with the product commands.
Done when: the repeat finishes and produces the plan's single completion fingerprint.

**Cassette 10.05 — Release proof and the build story.** Needs: 10.04.
Steps: run `test_l10_complete`. Update `BUILD_STORY.md` and `README.md` with what was measured,
including what did not meet its target. Push.
Done when: the test passes and everything is pushed; set REC-412 Done.
