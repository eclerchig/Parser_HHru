

function get_cloud_tokens() {
    var range1 = $("#range1").val();
    var range2 = $("#range2").val();
        $.ajax({
            data: [range1, range2], // get the form data
                url: "{% url 'update_clouds_tokens' %}",
                success: function (response) {
                        //
                },
                error: function (response) {
                    alert('Ошибка get_cloud_tokens()')
                }
            });
        return false;
    }