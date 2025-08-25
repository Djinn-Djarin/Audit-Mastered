<script>
    import { createEventDispatcher } from "svelte";
    import { onMount } from "svelte";
    import { toast } from "svelte-sonner";
    import {
        platforms,
        runAudit,
        stopAudit,
        auditSSE,
        deleteList,
        exportAudit,
        auditTaskIDs
    } from "../lib/utils.js";

    const dispatch = createEventDispatcher();

    export let list_id;
    export let list_name;
    export let created_at;
    export let platform;
    export let list_attributes={"Processed Items":0}
  

    let progress = 0;
    let auditId = null;
    let isAuditRunning = false;
    let reAudit = false;

    // ✅ Add reactive variables for display
    let currentCount = 0;
    let currentTotal = 0;

    $: selectedDetails = platforms.find((p) => p.name === platform);

    async function sendAuditRequest(list_id) {

        console.log(`reAudit is ${reAudit}`)
        const response = await runAudit(list_id, reAudit);
        auditId = response.task_id;

        if (response.status == "success"){
            toast.success(response.msg)
        }else{
            toast.error(response.msg)
        }
        
        isAuditRunning = true;
        await getAllAuditTaskIDs()
        streamAudit(auditId, list_id);

    }

    async function sendStopAuditRequest(list_id) {
        let tasks = JSON.parse(localStorage.getItem("audit_tasks")) || [];
        const task = tasks.find((t) => t.list_id === list_id);
        if (!task)
            return console.warn(`No running task for list_id ${list_id}`);

        const response = await stopAudit(task.task_id);

        tasks = tasks.filter((t) => t.list_id !== list_id);
        if (tasks.length > 0) {
            localStorage.setItem("audit_tasks", JSON.stringify(tasks));
        } else {
            localStorage.removeItem("audit_tasks");
        }

        if(response.status == "success"){
            toast.success(response.msg)
        }else{
            toast.error(response.msg)
        }
        isAuditRunning = false;
    }

    function streamAudit(task_id, component_list_id) {
        auditSSE(task_id, (update) => {
            // console.log("🔄 SSE update received:", update);
            list_attributes.count = update.count;
            list_attributes.product_count = update.total;
            if (component_list_id === list_id) {
                // ✅ update reactive vars
                currentCount = update.count;
                currentTotal = update.total;

                progress = Number(
                    ((update.count / update.total) * 100).toFixed(2),
                );

                if (progress >= 100) {
                    toast.success("Audit finished (progress 100%)");
                    isAuditRunning = false;
                }
            }
        })
            .then(() => {
                if (component_list_id === list_id) {
                    isAuditRunning = false;
                }
            })
            .catch((err) => {
                if (component_list_id === list_id) {
                    isAuditRunning = false;
                }
                toast.error("Audit error:", err);
            });
    }

    async function deleteListHandler(list_id){
        const res = await deleteList(list_id)
        if(res.status == "success"){
            toast.success(`${list_id} List Delected Successfully`)
        }
        dispatch("deleted", {list_id})
    } 

    async function downloadAudit(list_id) {
        try{

            let res = await exportAudit(list_id)
        }catch(err){
            let mes = JSON.parse(err.message)
            console.err(msg)
        }
    }

    onMount(() => {
        const tasks = JSON.parse(localStorage.getItem("audit_tasks")) || [];
        const myTask = tasks.find((t) => t.list_id === list_id);
        if (myTask) {
            isAuditRunning = true;
            streamAudit(myTask.task_id, list_id);
        }
    });

      async function getAllAuditTaskIDs() {
        const res = await auditTaskIDs(); // calls RunningAudits API
        console.log("Running audits from backend:", res);

        if (res?.running_audits?.length > 0) {
            localStorage.setItem(
                "audit_tasks",
                JSON.stringify(res.running_audits),
            );
        } else {
            localStorage.removeItem("audit_tasks");
        }
    }

</script>


<div
    class="rounded-xl p-5 shadow-md bg-white w-72 flex flex-col  space-y-4 transition"
    style="border-color: {selectedDetails
        ? selectedDetails.color
        : 'white'}; border-style: solid; border-width: 1px;"
>
    <!-- Header -->
    <div class="flex justify-between items-center">
        {#if selectedDetails}
            <div class="flex flex-col items-center">
                <img
                    src={selectedDetails.img}
                    alt={selectedDetails.name}
                    class="w-8 h-8 rounded-full shadow"
                />
            </div>
        {/if}

        <div>
            <div class="text-base font-semibold text-gray-800">
                {list_name.split(" ").slice(0, 3).join(" ")}{list_name.split(
                    " ",
                ).length > 3
                    ? "..."
                    : ""}
            </div>
        </div>

        <!-- Platform Logo -->

    </div>
    <div class="text-xs text-gray-500">
        {new Date(created_at).toLocaleString()}
    </div>
    <!-- Attributes -->
    <div class="space-y-2">
        {#each Object.entries(list_attributes) as [key, value]}
            <div class="flex justify-between text-sm">
                <span class="text-gray-600">{key}</span>
                <span class="font-medium text-gray-900">{value}</span>
            </div>
        {/each}
    </div>

    <!-- Actions -->
    <div class="flex justify-center space-x-6 pt-2 border-t border-gray-100">
        <button
            class="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-gray-900 transition"
            aria-label="download"
            onclick={() => downloadAudit(list_id)}
        >
            <i class="fa-solid fa-download"></i>
        </button>
        <!-- <button
            class="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-gray-900 transition"
            aria-label="edit"
        >
            <i class="fa-solid fa-edit"></i>
        </button> -->
        <button
            class="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-gray-900 transition"
            aria-label="delete"
            onclick={() => deleteListHandler(list_id)}
        >
            <i class="fa-solid fa-trash"></i>
        </button>
        <button
            class="p-2 rounded-lg hover:bg-gray-100 text-yellow-600 hover:text-yellow-700 transition"
            onclick={() => {
                reAudit =true, sendAuditRequest(list_id, reAudit);
            }}
        >
            <img src="/images/rotate_stop.png" alt="loop" class="h-5 w-5" />
        </button>
    </div>

    <!-- Progress Bar -->
    <div class="space-y-1 py-3">
        <div class="flex justify-between text-xs text-gray-500">
            <span>Progress</span>
            <span class="text-sm font-semibold text-gray-700">
                <span class="ml-1">{progress}%</span>
            </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
                class="h-2 rounded-full transition-all duration-500"
                style="width: {progress}%; background-color: {selectedDetails
                    ? selectedDetails.color
                    : '#3B82F6'}"
            ></div>
        </div>
    </div>

    <!-- Button styled with platform color -->
    <button
        class="w-32 mx-auto py-2 text-white rounded-lg font-semibold transition"
        style="background-color: {selectedDetails
            ? selectedDetails.color
            : '#4F46E5'}"
        onclick={() =>
            isAuditRunning
                ? sendStopAuditRequest(list_id)
                : sendAuditRequest(list_id, reAudit)}
    >
        {#if !isAuditRunning}
            Start Audit
        {:else}
            Stop Audit
        {/if}
    </button>
</div>

