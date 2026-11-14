"use strict";

const demoCase = document.querySelector("#demo-case");
const demoMethod = document.querySelector("#demo-method");
const demoSummary = document.querySelector("#demo-summary");
const demoTrace = document.querySelector("#demo-trace");
const demoCount = document.querySelector("#demo-count");

function number(value) {
  return value.toPrecision(7);
}

function showExample() {
  const run = ROOTLAB_EXAMPLES.find(item =>
    item.case === demoCase.value && item.method === demoMethod.value);
  demoTrace.replaceChildren();
  demoSummary.textContent = run.trace
    ? `x = ${number(run.root)} · Residual ${run.residual.toExponential(3)} · Reference error ${run.error.toExponential(3)} · ${run.updates} updates · ${run.inside ? "Inside" : "Outside"} assigned interval · ${run.status}`
    : `Run rejected: ${run.status}.`;
  for (const [index, [kind, x, residual]] of (run.trace || []).entries()) {
    const row = demoTrace.insertRow();
    for (const value of [index, kind, number(x), residual.toExponential(3)]) {
      row.insertCell().textContent = value;
    }
  }
  demoCount.textContent = run.trace ? `${run.trace.length} recorded points` : "No recorded points";
}

function selectCase() {
  const methods = ROOTLAB_EXAMPLES.filter(item => item.case === demoCase.value);
  demoMethod.replaceChildren(...methods.map(item => new Option(item.method)));
  showExample();
}

demoCase.addEventListener("change", selectCase);
demoMethod.addEventListener("change", showExample);
selectCase();
