static/script.js</code> sends the prompt to Flask and shows the answer:</p>
<!-- /wp:paragraph -->

<!-- wp:code -->
<pre class="wp-block-code"><code>async function sendPrompt() {
  const prompt = document.getElementById("prompt").value;
  const res = await fetch("/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  });
  const data = await res.json();
  document.getElementById("response").textContent =
    data.response || data.error || "No response.";
}
