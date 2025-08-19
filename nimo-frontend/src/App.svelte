<script>
  let imageUrl = "";
  let svg = "";
  let loading = false;
  let dailyArt = null;
  let dailyLoading = false;
  const api = "https://nimo.fly.dev";

  // Generate SVG from image URL
  async function generate() {
    loading = true;
    svg = "";
    try {
      const res = await fetch(`${api}/generate-svg`, {
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

  // Fetch daily art
  async function fetchDailyArt() {
    dailyLoading = true;
    try {
      const res = await fetch(`${api}/daily-art`);
      const data = await res.json();
      dailyArt = data;
    } catch (err) {
      console.error(err);
    }
    dailyLoading = false;
  }

  // Fetch daily art when component mounts
  fetchDailyArt();
</script>

<main class="p-4">
  <h1>Nimo</h1>
  
  <!-- Daily Art Section -->
  <div class="mb-8 p-4 bg-gray-50 rounded-lg">
    <h2 class="text-xl font-semibold mb-2">Nimo's Daily Creation</h2>
    {#if dailyLoading}
      <p class="text-gray-600">Loading today's creation...</p>
    {:else if dailyArt}
      <p class="text-sm text-gray-500 mb-3">{dailyArt.date}</p>
      <div class="border-2 border-gray-300 rounded-lg p-4 bg-white">
        <div class="flex justify-center">
          {@html dailyArt.svg}
        </div>
      </div>
    {:else}
      <p class="text-gray-600">Failed to load daily creation</p>
    {/if}
  </div>

  <!-- Image URL Input Section -->
  <div class="mb-8">
    <h2 class="text-xl font-semibold mb-2">Convert Image to SVG</h2>
    <input
      type="text"
      bind:value={imageUrl}
      placeholder="Enter image URL"
      class="border p-2 w-full rounded"
    />
    <button on:click={generate} class="mt-2 bg-black text-white px-4 py-2 rounded hover:bg-gray-800">
      {loading ? "Processing..." : "Generate SVG"}
    </button>
  </div>

  <!-- Generated SVG Result -->
  {#if svg}
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-2">Generated SVG</h2>
      <div class="border-2 border-gray-300 rounded-lg p-4 bg-white">
        {@html svg}
      </div>
    </div>
  {/if}
</main>

<style>
  :global(svg) {
    max-width: 100%;
    height: auto;
    max-height: 300px;
  }
  
  main {
    max-width: 800px;
    margin: 0 auto;
  }
  
  h1 {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 2rem;
  }
  
  h2 {
    color: #374151;
  }
  
  input {
    border-color: #d1d5db;
  }
  
  input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  button:hover {
    transition: background-color 0.2s;
  }
</style>
