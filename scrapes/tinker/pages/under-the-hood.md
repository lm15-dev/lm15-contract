# Under the Hood

This page explains some implementation details of Tinker, which are important for understanding how to speed up your code.

## Clock Cycles

In Tinker, after you call `ServiceClient.create_lora_training_client`, your training job gets assigned to a pool of machines that work together -- a *worker pool* -- which are doing forward-backward operations repeatedly in lock-step. Each of these steps of the worker pool is called a *clock cycle*. In each clock cycle, we do forward-backward and an optimizer step operation, each of which may involve multiple LoRA models that are being trained by this pool. You can think of this pool as a single large training run that is time-shared between multiple different LoRA models, often from different users.

With multi-tenancy -- sharing the same worker pool between multiple models -- we can run the training system efficiently even if users are training with small batch sizes, or if they have other delays in their training loops that would otherwise leave the worker pool idle. Small batch sizes can often give better *sample efficiency*, so this setup lets us achieve both high compute efficiency and high sample efficiency.

The downside is that it can sometimes lead to worse *latency*: even if training with a small batch, you'll still see the same step time as a large batch. (Still, note that we'll only charge you for the compute you use.) Also, if your training loop is implemented naively, you might have to wait multiple clock cycles per batch, because you might miss a clock cycle between operations.

### Overlapping `forward_backward` and `optim_step` Requests

Call `forward_backward` and `optim_step` without `await` to submit both requests, then await their returned futures. This way, they'll end up on the same clock cycle. If you write the code naively, you'll end up using *three* clock cycles per training step. Here's a recap of the example from the [Async Patterns](https://tinker-docs.thinkingmachines.ai/tutorials/basics/async-patterns/index.md) tutorial:

Here's the difference visually:

Cycle N Cycle N+1 Cycle N+2

Naive

fwd_bwd waiting... optim_step

Pipelined

fwd_bwd + optim — —

**❌ Naive implementation (uses 3 clock cycles):**

```python
# Submit forward_backward, gets queued for clock cycle N
fwd_bwd_future = client.forward_backward(batch, loss_fn)

# Wait for it to complete, and for client to receive the result
# Due to communication latency, this happens a little after cycle N+1 started
fwd_bwd_result = await fwd_bwd_future

# Submit optim_step, gets queued for clock cycle N+2
optim_future = client.optim_step(adam_params)

# Wait for it to complete, and for client to receive the result
# This happens a little after cycle N+2 finishes
optim_result = await optim_future

# Total: forward_backward on cycle N, optim_step on cycle N+2
# This takes 3 clock cycles (plus the time we waited before cycle N started)
```

**✓ Better implementation (uses 1 clock cycle):**

```python
# Submit both requests immediately. They'll both be slotted into the same clock cycle N
fwd_bwd_future = client.forward_backward(batch, loss_fn)
optim_future = client.optim_step(adam_params)

# Now wait for results - both operations happen on cycle N
fwd_bwd_result = await fwd_bwd_future
optim_result = await optim_future

# Total: both operations on cycle N
# This takes 1 clock cycle
```

### Pipelining to Maximize Clock Cycle Efficiency

To maximize efficiency and avoid missing clock cycles, you should **pipeline your training loop**: submit the next batch before waiting for the current batch to complete. This ensures there's always a request queued when a new clock cycle starts.

Cycle 1 Cycle 2 Cycle 3 Cycle 4

Non-pipelined

batch 1 gap batch 2 gap

Pipelined

batch 1 batch 2 batch 3 batch 4

**Non-pipelined**: Submits a batch, waits for it to complete, then submits the next. This wastes clock cycles because there's a gap between when one batch finishes and the next is submitted — typically using 2 clock cycles per training step.

**Pipelined**: Submits the next batch *before* waiting for the previous batch to complete. This uses exactly 1 clock cycle per step, achieving maximum efficiency.

For hands-on examples of pipelined training, see the [Your First SFT](https://tinker-docs.thinkingmachines.ai/tutorials/basics/first-sft/index.md) and [SFT with Config](https://tinker-docs.thinkingmachines.ai/tutorials/cookbook-abstractions/sft-with-config/index.md) tutorials. For concurrent sampling patterns, see [Async Patterns](https://tinker-docs.thinkingmachines.ai/tutorials/basics/async-patterns/index.md).

## Avoid Client-Side Timeouts and Retries

A common failure mode is wrapping Tinker requests in your own timeout logic (e.g. `asyncio.wait_for` around `sampling_client.sample(...)`), often combined with retries. **Don't do this.** The SDK and backend already handle retries for transient failures, and the SDK detects truly stuck requests. Adding your own timeouts and retries on top creates several footguns:

- **Latency varies with load.** Tinker is optimized for throughput rather than latency, and request latency depends on the overall load on the system and on your generation length. A request that normally takes a minute can legitimately take much longer when the samplers are busy. There's no fixed "correct" timeout value.
- **Timeouts turn slowness into total failure.** If the backend is busy and every request in a batch exceeds your timeout, your job makes *zero* progress, no matter how many times you retry. Without the timeout, the same job would have run slightly slower but kept making progress.
- **Retries amplify load.** Cancelling and resubmitting requests adds more work to an already-busy system, making the slowness worse for you and everyone else.
- **Duplicated retry logic interacts badly.** The SDK already retries transient errors internally. Client-side retries stacked on top can multiply the number of in-flight requests and make failures harder to debug (on our side, we just see a bunch of cancellations).

This applies especially to RL sampling loops (e.g. GRPO), where it's tempting to bound each batch's sampling time. Instead of a per-request timeout, submit all your sampling requests concurrently and wait for them; slow steps will resolve on their own. If sampling speed is dramatically blocking your training jobs, please [email support](https://tinker-docs.thinkingmachines.ai/support/index.md) with your session ID rather than working around it with timeouts.
