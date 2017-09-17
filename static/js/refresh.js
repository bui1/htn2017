function refresh() {
    $.ajax({
	url: "/chat-recv",
	success: function(text) {
	    $("#chat").append($("<div class='msg_b'>" + text + "</div>"));
	}
    })
};

refresh();
setInterval(refresh, (1*1000));
</script>
