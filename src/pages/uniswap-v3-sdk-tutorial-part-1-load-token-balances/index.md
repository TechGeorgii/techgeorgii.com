---
layout: ../../layouts/ArticleLayout.astro
title: "Uniswap V3 SDK Swap Tutorial 1/5 – Load token balances"
description: "This is the first part of Uniswap V3 SDK Swap Tutorial, full source code In this part of tutorial we’ll create TypeScript application and connect to Ethereum-compatible blockchain to load token balances. For the sake of "
pubDate: "2022-07-13"
---

This is the first part of [Uniswap V3 SDK Swap Tutorial](/uniswap-v3-sdk-tutorial/), [full source code](https://github.com/TechGeorgii/uniswap-v3-sdk-tutorial-ts)

In this part of tutorial we’ll create TypeScript application and connect to Ethereum-compatible blockchain to load token balances. For the sake of simplicity, we’ll omit “import” statements, parametrising the program by command line arguments and environment variables (you can find full version on [Github](https://github.com/TechGeorgii/uniswap-v3-sdk-tutorial-ts)).

### ethers.js initialization

Below are the parameters we need to run a swap. They are pretty self-explanatory, for an API to blockchain we’ll use [Alchemy](https://alchemy.com). Don’t save these addresses and keys in the code! ***inAmountStr*** is a string representing the amount of ***tokenIn*** (identified by ***tokenInContractAddress***) you’d swap to get ***tokenOut*** (represented by ***tokenOutContractAddress***). ***walletAddress*** is where to take your funds.

```typescript
const chainId = 5;  // chainId for Goerli
const walletAddress = "0xAAaaa...AA";
const tokenInContractAddress = "0xBbbbBb...bbBbb";
const tokenOutContractAddress = "0xCccCCc...ccc";
const inAmountStr = "0.0001";
const API_URL = "https://eth-goerli.alchemyapi.io/v2/XXXXXXXXXXXXXXXXXX";
const PRIVATE_KEY = "000000000000000000";
```

As test network I’d recommend to use Matic (Polygon). I’ve tried Rinkeby, Ropsten, they are deprecated but still work. Alchemy recommends to use Goerli, but for Goerly as of July 2022 only WETH-UNI pair is available.

Then follows initialization of [ethers.js](https://docs.ethers.io/) ***provider*** (think about it as interface to certain Ethereum network) and ***signer*** (that’s what will sign transactions you’ll send to blockchain). This tutorial is a console application, so we use Alchemy API to query blockchain and private key of your ***walletAddress*** to sign messages:

```typescript
const provider = new ethers.providers.JsonRpcProvider(API_URL, chainId);
const signer = new ethers.Wallet(PRIVATE_KEY!, provider);
```

For a React application if you use Metamask to send transactions and to sign messages, the following initialization should be used:

```typescript
const ethereum = (window as any).ethereum;
const accounts = await ethereum.request({
    method: "eth_requestAccounts",
});
const provider = new ethers.providers.Web3Provider(ethereum);
const walletAddress = accounts[0];
const signer = provider.getSigner(walletAddress);
```

So, ***walletAddress*** is chosen by Metamask and signer initialised automatically as Metamask knows your private key.

### Loading token balances

Next step is straightforward. Here we create ethers.js contracts to load token balances and tokens’ properties:

```typescript
const contractIn = new ethers.Contract(tokenInContractAddress, ERC20_abi, signer);
const contractOut = new ethers.Contract(tokenOutContractAddress, ERC20_abi, signer);

const getTokenAndBalance = async function (contract: ethers.Contract) {
    var [dec, symbol, name, balance] = await Promise.all(
        [
            contract.decimals(),
            contract.symbol(),
            contract.name(),
            contract.balanceOf(walletAddress)
        ]);

    return [new Token(chainId, contract.address, dec, symbol, name), balance];
}

const [tokenIn, balanceTokenIn] = await getTokenAndBalance(contractIn);
const [tokenOut, balanceTokenOut] = await getTokenAndBalance(contractOut);

console.log(`Wallet ${walletAddress} balances:`);
console.log(`   Input: ${tokenIn.symbol} (${tokenIn.name}): ${ethers.utils.formatUnits(balanceTokenIn, tokenIn.decimals)}`);
console.log(`   Output: ${tokenOut.symbol} (${tokenOut.name}): ${ethers.utils.formatUnits(balanceTokenOut, tokenOut.decimals)}`);
console.log("");
```

Probably, only ***ERC20\_abi*** should be explained. It is a JSON that describes ERC-20 smart contract methods so ethers.js can call them. Both our ***tokenInContractAddress*** and ***tokenOutContractAddress*** are ERC-20 token smart contracts. [Here you can find](https://github.com/TechGeorgii/uniswap-v3-sdk-tutorial-ts/blob/main/ERC20_abi.json) that JSON. It is imported at the top of the source file as:

```typescript
import ERC20_abi from "./ERC20_abi.json"
```

Here it is. You finished the first part of Uniswap V3 SDK Swap Tutorial, you’re awesome! We pulled token properties and printed their balances. We didn’t do anything with Uniswap tho, but prepared a solid foundation for the next part – [Part 2 – Get pool information](/uniswap-v3-sdk-swap-tutorial-part-2-get-pool-information/).

If anything is unclear please write a comment and I’ll try to answer.
