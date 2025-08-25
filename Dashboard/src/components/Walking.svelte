<script>
  import { onMount } from "svelte";
  import lottie from "lottie-web";

  export let src;
  export let speed = 0.5;
  export let loop = true;
  export let autoplay = true;
  export let hoverPause = false;

  let el;
  let anim;

  // Run once on mount
  onMount(() => {
    return () => anim?.destroy(); // cleanup on unmount
  });

  // Reactive block: reload animation whenever src changes
  $: if (src && el) {
    // destroy previous animation if exists
    anim?.destroy();

    anim = lottie.loadAnimation({
      container: el,
      renderer: "svg",
      loop,
      autoplay,
      path: src,
    });

    anim.setSpeed(speed);

    if (hoverPause) {
      el.addEventListener("mouseenter", () => anim.pause());
      el.addEventListener("mouseleave", () => anim.play());
    }
  }
</script>

<div bind:this={el} class="bg-white w-full h-full"></div>
