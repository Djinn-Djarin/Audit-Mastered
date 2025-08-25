<script>
    import { goto } from "$app/navigation";
  import Walking from "../components/Walking.svelte";
  let src = '/images/Cat playing animation.json'
</script>
<div class="flex items-center justify-center w-screen h-screen overflow-hidden">
  <!-- Floating wrapper -->

       <Walking src={src} />


  <button class="absolute flex top-[10%] left-1/2 -translate-x-1/2  p-4 text-3xl  rounded-lg"
   onclick={() => goto('/')}
  >
    Go to Home
  </button>
</div>
