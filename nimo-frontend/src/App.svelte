<script>
  let imageUrl = "";
  let svg = "";
  let loading = false;
  const api = "https://nimo.fly.dev/generate-svg";

  // Generate SVG from image URL
  async function generate() {
    loading = true;
    svg = "";
    try {
      const res = await fetch(api, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_url: imageUrl,
          width_mm: 160,
          height_mm: 160,
          margin_mm: 5,
          simplify_mm: 0.2,
          mode: "outline",
        }),
      });
      const data = await res.json();
      svg = data.svg;
    } catch (err) {
      console.error(err);
    }
    loading = false;
  }
</script>

<main class="p-4">
  <h1>Nimo</h1>
  <input
    type="text"
    bind:value={imageUrl}
    placeholder="Enter image URL"
    class="border p-2 w-full"
  />
  <button on:click={generate} class="mt-2 bg-black text-white px-4 py-2">
    {loading ? "Processing..." : "Generate SVG"}
  </button>

  {#if svg}
    <h2 class="mt-4">Result</h2>
    <div class="border mt-2 p-2">
      {@html svg}
    </div>
  {/if}
</main>
