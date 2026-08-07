---
source: Graph-Engineering-Andrew-Ng-Playbook.pdf
fetched: 2026-08-05
pages: 2-4
---
> **In here:** Reflection, Tool Use, Planning, Multi-Agent Collaboration · Failure modes and controls per pattern · Ng's maturity assessment (Table I)

# II. The Four Design Patterns

## A. Step 1: Reflection

Reflection is an iterative process in which an LLM examines an output, compares it with a task or rubric, identifies defects, and produces a revision. The pattern can be implemented with one model instance alternating between generator and critic prompts, or with two role-separated instances. The important property is not the number of model objects — it is the presence of an explicit feedback loop and a stopping rule.

```python
@dataclass
class Critique:
    satisfactory: bool
    issues: list[str]
    revision_instructions: list[str]

def reflect(task, llm, max_iterations=3):
    draft = llm.generate(task)
    for _ in range(max_iterations):
        feedback = llm.evaluate(task=task, draft=draft)
        if feedback.satisfactory:
            return draft
        draft = llm.revise(task, draft, feedback)
    return draft
```

Ng's coding example is direct: a coder agent writes code, then receives a critique prompt. The evaluator often catches bugs, missing edge cases, or poor structure that the first pass overlooked. Ng reports: "I've been delighted by how much it improved my applications' results" and describes reflection as "pretty robust technology — I can almost always get them to work well."

Failure modes: (1) Self-confirmation — the critic repeats assumptions that produced the draft. (2) Rubric drift — the evaluator rewards fluency instead of correctness. (3) Non-monotonic revision — a fix introduces another bug. Controls: keep an immutable task statement, compare every revision against the rubric, run deterministic checks before subjective evaluation, cap iterations.

The first practical tip is to separate critique from rewriting. Do not ask "improve this" and accept an opaque replacement. Request a structured list of issues first, then feed that list into a distinct revision step. The second tip is to make the evaluator cite evidence from the draft, tests, or source material. A critique that says "the function might not handle edge cases" is less useful than one that says "line 12 does not handle the case where the input list is empty, which violates requirement 3 in the specification." The third tip is to store every intermediate artifact — draft, critique, revision, and stopping decision — so that engineers can diagnose whether failures came from weak generation, weak evaluation, or a faulty stopping rule. Without this record, debugging a reflection loop is like debugging a program without logs.

## B. Step 2: Tool Use

Tool Use allows an LLM to select and call external capabilities: web search, code execution, databases, APIs. The model contributes language understanding and decision making; the tool contributes grounded data or deterministic action. Ng observes that early tool-use work came from the computer vision community because language models could not directly manipulate images — "the only option was that the LLM generate a function call." A model that can execute code can verify its own logic. A model that can search can ground its claims. Tool use transforms an LLM from a closed system into one that can check its work against reality.

```python
@dataclass
class ToolCall:
    name: str
    arguments: dict

tools = {
    "web_search": search_web,
    "run_code": execute_python,
    "query_db": database_query,
}

def agent_with_tools(task, llm, tools, max_steps=10):
    context = [task]
    for _ in range(max_steps):
        action = llm.choose_action(context, tools)
        if action.name == "finish":
            return llm.synthesize(context)
        result = tools[action.name](**action.arguments)
        context.append({"tool": action.name,
                        "result": result})
    return llm.synthesize(context)
```

Failure modes: (1) Wrong tool selection — calling a search when a database query is needed. (2) Invalid arguments — passing malformed inputs that the tool cannot process. (3) Trusting tool output blindly — not validating that a search result is relevant or that code execution produced the expected output type. (4) Tool overuse — calling tools when sufficient context already exists in the window, wasting tokens and latency. Controls: typed tool schemas with validated arguments, result confirmation before incorporation, permission boundaries that separate read from write access, and retry limits that prevent infinite tool-call loops.

## C. Step 3: Planning

Planning uses an LLM to autonomously decide what sequence of steps to execute. Ng describes a live demo where his research agent's web search API returned a rate-limiting error: "To my surprise, the agent pivoted deftly to a Wikipedia search tool — which I had forgotten I'd given it — and completed the task." Ng's maturity assessment is explicit: "more emerging — sometimes my mind is blown by how well they work, but at least at this moment in time, I don't feel like I can always get them to work reliably." Planning agents therefore need tighter constraints: structured plan formats, dependency validation, bounded step counts, and fallback policies.

```python
def plan_and_execute(objective, llm, tools, budget):
    plan = llm.create_plan(objective)  # JSON steps
    results = []
    for step in plan.steps:
        result = execute_step(step, tools, results)
        results.append(result)
        if result.failed:
            plan = llm.replan(
                objective, results,
                remaining_budget=budget)
    return llm.synthesize(results)
```

The code illustrates the critical pattern: when a step fails, *the agent replans with context of what already worked.* This is the "preserve successful work across replans" principle. Without it, a failure at step 5 of 8 discards the successful results of steps 1–4 and starts over, wasting both tokens and time. With it, the replan builds on established ground.

Ng also mentions using research agents for his own work: "one piece of research that I don't feel like Googling myself — I send it to the research agent, come back in a few minutes and see what it's come up with." This captures the operational reality of planning agents: they are most useful when the human's time is more expensive than the agent's tokens, and when the task is well-defined enough that the agent's plan can be evaluated against objective criteria. Open-ended research ("find something interesting") produces plans that are hard to evaluate and easy to waste tokens on; focused research ("find all papers citing X that report Y") produces plans that are straightforward to validate.

Failure modes: (1) Over-planning — generating elaborate plans for simple tasks that a single call could handle. (2) Plan-execution gap — the plan describes steps the agent cannot actually perform with its available tools. (3) Cascading failure — one bad step corrupts all subsequent steps because they depend on its output. (4) Unbounded replanning — the agent replans indefinitely without converging on a solution. Controls: validate dependencies before execution (can every step's inputs be produced by a prior step or a tool?), preserve successful work across replans, bound total steps, and define explicit failure criteria ("if step fails twice after replan, escalate to human rather than trying a third time").

## D. Step 4: Multi-Agent Collaboration

Multi-Agent Collaboration involves multiple LLM instances, each prompted with different roles, working together on tasks that benefit from specialization. Ng's ChatDev example: "completely open source, runs on my laptop." The system prompts one LLM to act as CEO, another as designer, another as product manager, another as tester. "This flock of agents collaborate — if you tell it 'please develop a Go game,' they'll actually spend a few minutes writing code, testing it, iterating, and then generate surprisingly complex programs."

Ng calls multi-agent collaboration "more emerging" but says it "works much better than you might think." The practical tip: define an artifact contract for every handoff. The researcher returns claims with sources. The planner returns typed steps. The coder returns code and assumptions. The evaluator returns defects and a decision. Agents should communicate through artifacts and shared state, not unlimited conversational history. This constraint prepares the system for graph architecture.

Multi-agent debate — having different agents argue different positions — "actually results in better performance as well." The mechanism is straightforward: when two agents with different role prompts examine the same evidence, they tend to catch different error classes. A coder agent optimizes for functionality; a reviewer agent optimizes for edge cases; a tester agent optimizes for coverage. No single rubric captures all three — but three agents with three rubrics approximate a team. The practical limitation is cost: three agents consume three times the tokens, and if all three see the same evidence and optimize the same weak rubric, the system reproduces the same error three times at higher cost. The test for whether to add an agent: does this role catch an error class that existing roles demonstrably miss?

### Table I — Pattern Maturity Assessment (Andrew Ng)

| Pattern | Maturity | Ng's Assessment |
| --- | --- | --- |
| Reflection | Robust | "I can almost always get them to work well" |
| Tool Use | Robust | Widely deployed, well-understood |
| Planning | Emerging | "Less mature, less predictable" |
| Multi-Agent | Emerging | "Works much better than you might think" |
