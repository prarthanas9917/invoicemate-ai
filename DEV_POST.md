---
title: "InvoiceMate AI: a private expense helper for freelancers"
published: false
tags: devchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12).*

## What I Built

InvoiceMate AI is a small expense-organizing app for freelancers and small
business owners. Paste receipt text or upload a text-based PDF/TXT file, review
the fields it extracts, and export the expenses as a CSV.

I wanted to make the repetitive part of bookkeeping a little less tedious
without asking people to send financial documents to another company's AI
service. This is an early MVP: saved expenses last for the current session,
scanned PDFs need OCR that is not included yet, and the extracted details
should always be checked by a person.

## Demo

**Before publishing:** run the app locally and add a short screen recording or
screenshots here. The app is designed to run on the user's computer, so I have
not represented it as a hosted service.

## Code

**Before publishing:** create the public GitHub repository named
`invoicemate-ai`, push this project, and replace the link below if you choose a
different repository name.

https://github.com/prarthanas9917/invoicemate-ai

## How I Built It

The interface is Python and Streamlit. pypdf reads selectable text from PDFs,
and pandas builds the expense table and CSV export. Ollama serves Qwen 2.5 3B
locally, and the model returns the fields as JSON for the user to review.

To try it, install Ollama, run `ollama pull qwen2.5:3b`, install
`requirements.txt`, and start the app with `streamlit run app.py`. The full
instructions are in the repository README.

## Why Does Open Innovation Matter?

An invoice can reveal more than a purchase: it may include a client's name,
address, or other business details. With local inference, InvoiceMate sends
the document text to Ollama on the same computer instead of a hosted AI API.
After the model is downloaded, it can work offline, and there is no per-receipt
AI API charge. I can also replace the model without rebuilding the app around
a single provider.

That does not make the model infallible or remove the need for a capable
computer. The app deliberately asks people to review the result before saving
it. For this use case, the privacy and predictable running cost are worth the
extra local setup.

## Before You Publish

- Run the app and include a real screenshot or screen recording in the Demo
  section.
- Create and push the GitHub repository, then verify the Code link.
- Add a First User section only if someone has actually tried it; describe
  their feedback accurately.
- Check the challenge page for current partner categories before listing any.
- Verify the challenge deadline and eligibility requirements.
