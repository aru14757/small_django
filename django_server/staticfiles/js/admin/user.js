(function($) {
    $(document).ready(function() {
        function toggleMentorManagerFields() {
            var role = $('#id_role').val();
            if (role === 'employee') {
                $('#id_mentor').closest('.form-row').show();
                $('#id_manager').closest('.form-row').show();
            } else {
                $('#id_mentor').closest('.form-row').hide();
                $('#id_manager').closest('.form-row').hide();
            }
        }

        // Initial call to hide/show fields
        toggleMentorManagerFields();

        // Trigger toggle on role change
        $('#id_role').change(function() {
            toggleMentorManagerFields();
        });
    });
})(django.jQuery);
