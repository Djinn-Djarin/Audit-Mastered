<script>
    import { goto } from "$app/navigation";

</script>
<div class="relative w-screen h-screen overflow-hidden">
  <!-- Floating wrapper -->
  <div class="animate-float-small w-full h-full">
    <img 
      src="/images/404.png" 
      alt="404"
      class="w-full h-full object-cover"
    />
  </div>

  <button class="absolute flex top-[75%] left-1/2 -translate-x-1/2 underline p-4 text-xl text-pink-400 rounded-lg"
   onclick={() => goto('/')}
  >
    Go to Home
  </button>
</div>
