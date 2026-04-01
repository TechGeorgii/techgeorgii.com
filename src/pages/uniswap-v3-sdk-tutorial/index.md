---
layout: ../../layouts/ArticleLayout.astro
title: "Uniswap V3 SDK Swap Tutorial"
description: "First of all, a short Q&A. What is Uniswap? Uniswap (Uniswap protocol) is a DeFi (Decentralised Finance) application and protocol that swaps tokens. E.g. you have an ETH and you want to get USDT that’s – that’s swap. The"
pubDate: "2022-07-13"
---

First of all, a short Q&A.

**What is Uniswap?**

[Uniswap](https://uniswap.org) (Uniswap protocol) is a DeFi (Decentralised Finance) application and protocol that swaps tokens. E.g. you have an ETH and you want to get USDT that’s – that’s swap. The beauty is that Uniswap is decentralized, not controlled by anyone and lives on blockchain.

**Why another Uniswap tutorial?**

I wanted to implement swap functionality with Uniswap and was looking for Uniswap V3 SDK example, and it turned out (a) there are lack of examples on the Internet (b) [official docs](https://docs.uniswap.org/sdk/introduction) have an example of Uniswap V3 SDK, but there are lot of practical concepts up there that are not explained detailed enough for a newcomer.

In this example V3 SDK version is used. [Source code](https://github.com/TechGeorgii/uniswap-v3-sdk-tutorial-ts) is in TypeScript. Module syntax is used so that you can copy this code in both console and React apps. Please note this code can’t be considered production-ready. Tutorial consists of 5 parts for clarity:

- [Part 1 – Load token balances](/uniswap-v3-sdk-tutorial-part-1-load-token-balances/)
- [Part 2 – Get pool information](/uniswap-v3-sdk-swap-tutorial-part-2-get-pool-information/)
- [Part 3 – Get quotes with Uniswap Quoter](/uniswap-v3-sdk-swap-tutorial-part-3-get-quotes-with-uniswap-quoter/)
- [Part 4 – Get swap route](/uniswap-v3-sdk-swap-tutorial-part-4-get-swap-route/)
- [Part 5 – Make actual swap with Uniswap](/uniswap-v3-sdk-swap-tutorial-part-5-execute-a-swap/)
