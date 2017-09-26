$.notify.addStyle("metro", {
    html:
        "<div>" +
            "<div class='image' data-notify-html='image'/>" +
            "<div class='text-wrapper'>" +
                "<div class='title' data-notify-html='title'/>" +
                "<div class='text' data-notify-html='text'/>" +
            "</div>" +
        "</div>",
    classes: {
        default: {
            "color": "#fafafa !important",
            "background-color": "#ABB7B7",
            "border": "1px solid #ABB7B7"
        },
        error: {
            "color": "#fafafa !important",
            "background-color": "#d74548",
            "border": "1px solid #cb2a2a"
        },
        success: {
            "color": "#fafafa !important",
            "background-color": "#34c73b",
            "border": "1px solid #33b86c"
        },
        info: {
            "color": "#fafafa !important",
            "background-color": "#3fb7ee",
            "border": "1px solid #1ca8dd"
        },
        warning: {
            "color": "#fafafa !important",
            "background-color": "#f7c836",
            "border": "1px solid #ebc142"
        },
        black: {
            "color": "#fafafa !important",
            "background-color": "#2f353f",
            "border": "1px solid #14082d"
        },
        white: {
            "background-color": "#e6eaed",
            "border": "1px solid #ddd"
        }
    }
});