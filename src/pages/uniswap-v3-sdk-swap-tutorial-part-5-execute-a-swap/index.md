---
layout: ../../layouts/ArticleLayout.astro
title: "Uniswap V3 SDK Swap Tutorial 5/5 – Execute a swap"
description: "This is the part 5 of Uniswap V3 SDK Swap Tutorial, full source code. In this part of the tutorial we will make actual swap having a route we obtained from Uniswap in previous part. Approving token for Uniswap to spend T"
pubDate: "2022-07-29"
---

This is the part 5 of [Uniswap V3 SDK Swap Tutorial](/uniswap-v3-sdk-tutorial/), [full source code](https://github.com/TechGeorgii/uniswap-v3-sdk-tutorial-ts). In this part of the tutorial we will make actual swap having a route we obtained from Uniswap in [previous part](/uniswap-v3-sdk-swap-tutorial-part-4-get-swap-route/).

### Approving token for Uniswap to spend

There is a important nuance we need to handle. While Uniswap (and more precisely, Uniswap router smart contract) executes your swap, it takes some amount of input token from your wallet. We need to authorise this operation by calling [**approve** function](https://ethereum.org/en/developers/docs/standards/tokens/erc-20/) on our input token as the following pseudocode:

> tokenIn.approve(UNISWAP\_ROUTER\_ADDRESS, Amount\_to\_approve)

As this would be a blockchain state-changing transaction, it requires some gas. There are two options in terms of user approval. If you use Metamask as provider (as explained in [Part 1](/uniswap-v3-sdk-tutorial-part-1-load-token-balances/)) than it would be just one line call to input token smart contract. As usually, address of Uniswap router and other contracts can be found [here](https://docs.uniswap.org/protocol/reference/deployments):

```typescript
// address of a swap router
const V3_SWAP_ROUTER_ADDRESS = '0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45';
await contractIn.approve(V3_SWAP_ROUTER_ADDRESS, amountIn);
```

Metamask will show a popup window where you need to confirm transaction and agree on gas price (or set your own).

If provider is a JsonRpcProvider (and you use service like Alchemy) then we would need to construct transaction manually. This is a good thing to understand the internals:

```typescript
// here we just create a transaction object (not sending it to blockchain).
const approveTxUnsigned = await contractIn.populateTransaction.approve(V3_SWAP_ROUTER_ADDRESS, amountIn);
// by default chainid is not set https://ethereum.stackexchange.com/questions/94412/valueerror-code-32000-message-only-replay-protected-eip-155-transac
approveTxUnsigned.chainId = chainId;
// estimate gas required to make approve call (not sending it to blockchain either)
approveTxUnsigned.gasLimit = await contractIn.estimateGas.approve(V3_SWAP_ROUTER_ADDRESS, amountIn);
// suggested gas price (increase if you want faster execution)
approveTxUnsigned.gasPrice = await provider.getGasPrice();
// nonce is the same as number previous transactions
approveTxUnsigned.nonce = await provider.getTransactionCount(walletAddress);

// sign transaction by our signer
const approveTxSigned = await signer.signTransaction(approveTxUnsigned);
// submit transaction to blockchain
const submittedTx = await provider.sendTransaction(approveTxSigned);
// wait till transaction completes
const approveReceipt = await submittedTx.wait();
if (approveReceipt.status === 0)
    throw new Error("Approve transaction failed");
```

Basically, you can understand what happens from the comments.

**IMPORTANT!** One thing to note is that in this tutorial, for logical purposes, ***approve*** call is put after we got the swap route and before submitting this route for execution to make a swap. ***In real world you would want to make time interval between getting a route and executing a swap to be as short as possible*** to be as close as possible to route parameters since pool state can change.

### Sending a swap transaction to Uniswap

Then we create a swap transaction:

```typescript
const value = BigNumber.from(route.methodParameters.value);

const transaction = {
    data: route.methodParameters.calldata,
    to: V3_SWAP_ROUTER_ADDRESS,
    value: value,
    from: walletAddress,
    gasPrice: route.gasPriceWei,

    // route.estimatedGasUsed might be too low!
    // most of swaps I tested fit into 300,000 but for some complex swaps this gas is not enough.
    // Loot at etherscan/polygonscan past results.
    gasLimit: BigNumber.from("800000")
};

var tx = await signer.sendTransaction(transaction);
const receipt = await tx.wait();
if (receipt.status === 0) {
    throw new Error("Swap transaction failed");
}
```

The code should be clear – we construct transaction, submit it to blockchain and wait till it completes.

An important note, **gasLimit** in theory can be initialised by **route.estimatedGasUsed** ([part 4](/uniswap-v3-sdk-swap-tutorial-part-4-get-swap-route/)) and that would work, but sometimes estimated gas limit is not precise enough and transaction fails.

My experiments demonstrated most of my transactions fall below 800,000 gasLimit, so I set it as a limiting value. But it really depends on number of swap hops so you might need to set another limit based on your needs up to max possible gas limit (https://etherscan.io/blocks can be referred to see current max gas limit for a block).

In theory, when you use Web3Provider with Metamask (as explained in [Part 1](/uniswap-v3-sdk-tutorial-part-1-load-token-balances/)), Metamask should estimate **gasLimit** automatically. But in practice **UNPREDICTABLE\_GAS\_LIMIT** error is thrown by ethers.js (transaction is complex and [limit can’t be estimated](https://docs.ethers.io/v5/troubleshooting/errors/#help-UNPREDICTABLE_GAS_LIMIT)).

That’s it, we finished all parts and successfully made a swap! You can now load and print tokens’ balances to see new ones (refer to [Part 1](/uniswap-v3-sdk-tutorial-part-1-load-token-balances/) on how to do it).

Full TypeScript source code is on [Github](https://github.com/TechGeorgii/uniswap-v3-sdk-tutorial-ts). Please note that tutorial code is not production ready, with almost no error handling, so it is just for demonstration purposes.

If there are any questions please let me know in the comments section and I’ll try to answer.

[Link to all parts of this tutorial](https://techgeorgii.com/uniswap-v3-sdk-tutorial/).

Happy coding!
