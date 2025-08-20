export function load({ fetch }) {
       const lists = [
        {
            list_id: "list_id",
            list_name: "Amazon Audit",
            created_at: "2023-10-01T12:00:00Z",
            platform: "amazon",
            list_attributes: {
                product_count: 10000,
                Live: 530,
                "Supressed Asin Changed": 260,
                "Supressed Page Timeout": 56,
            },
            isReviewed: false,
            progress: 65,
        },
        {
            listName: "Flipkart QA",
            timeStamp: "2023-11-15T08:00:00Z",
            selectedPlatform: "flipkart",
            listAttributes: {
                totalCount: 5000,
                Live: 420,
                "Supressed Asin Changed": 120,
                "Supressed Page Timeout": 25,
            },
            isReviewed: true,
            progress: 80,
        },
        {
            listName: "Myntra List",
            timeStamp: "2023-09-20T18:30:00Z",
            selectedPlatform: "myntra",
            listAttributes: {
                totalCount: 8000,
                Live: 300,
                "Supressed Asin Changed": 95,
                "Supressed Page Timeout": 15,
            },
            isReviewed: false,
            progress: 40,
        },
        {
            listName: "Swiggy List",
            timeStamp: "2023-09-20T18:30:00Z",
            selectedPlatform: "swiggy",
            listAttributes: {
                totalCount: 8000,
                Live: 300,
                "Supressed Asin Changed": 95,
                "Supressed Page Timeout": 15,
            },
            isReviewed: false,
            progress: 40,
        },
        {
            listName: "Zepto List",
            timeStamp: "2023-09-20T18:30:00Z",
            selectedPlatform: "zepto",
            listAttributes: {
                totalCount: 8000,
                Live: 300,
                "Supressed Asin Changed": 95,
                "Supressed Page Timeout": 15,
            },
            isReviewed: false,
            progress: 40,
        },
    ];
    return {
        lists
    };
}