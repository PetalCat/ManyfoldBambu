<script lang="ts">
  import "../app.css";

  let { children } = $props();
</script>

<svelte:head>
  <!-- No favicon needed for extension popup -->
</svelte:head>

{@render children?.()}
