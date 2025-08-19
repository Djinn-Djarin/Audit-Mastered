<script>
    import ListModal from "../components/ListModalStatus.svelte";
    import ListModalAdd from "../components/ListModalAdd.svelte";
    import Header from "../components/Header.svelte";
    import Footer from "../components/Footer.svelte";
      const videoSrc = '/videos/lofi-animation.mp4';
    // data passed from +page.js
    export let data;
    const { lists } = data;

    let isAddList = false;

    function toggleAddList() {
        isAddList = !isAddList;
    }
</script>

<div class="flex flex-col min-h-screen bg-gray-100">
    <!-- Header always on top -->
    <Header />

    <!-- Main content grows to push footer down -->
    <main
        class="flex-1 flex flex-wrap gap-6 px-6 py-10 items-start justify-center"
    >
        {#each lists as list}
            <ListModal {...list} />
        {/each}

        <!-- Add List Button -->
    </main>

    <button
        on:click={toggleAddList}
        class=" absolute top-180 right-30 rounded-full h-20 w-20 flex items-center justify-center shadow-md bg-white hover:bg-gray-50 transition border border-dashed border-gray-400 floating-btn"
    >
        <img
            src="/images/plus.png"
            alt="Add list"
            class="w-10 h-10 items-center"
        />
    </button>

    <!-- Modal Overlay -->
    {#if isAddList}
        <div class="fixed inset-0 flex items-center justify-center z-50">
            <!-- Overlay background -->
            <div
                class="absolute inset-0 bg-gray-400/80 shadow-lg"
                on:click={() => (isAddList = false)}
            ></div>

            <!-- Modal Content -->
            <div class="relative z-10">
                <div class="bg-white rounded-lg p-6">
                    <ListModalAdd on:close={() => (isAddList = false)} />
                </div>
            </div>
        </div>
    {/if}

    <!-- Footer always pinned to bottom -->
    <Footer />
</div>
<style>
    /* Floating animation */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-60px); }
        100% { transform: translateY(0px); }
    }

    .floating-btn {
        animation: float 30s ease-in-out infinite;
    }
</style>