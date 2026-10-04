document.addEventListener("DOMContentLoaded", function () {

    // Confirm before logout
    const logoutLinks = document.querySelectorAll(".logout");

    logoutLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {

            const confirmLogout = confirm("Are you sure you want to logout?");

            if (!confirmLogout) {
                event.preventDefault();
            }
        });
    });


    // Appointment date validation
    const appointmentDate = document.querySelector(
        'input[name="appointment_date"]'
    );

    if (appointmentDate) {

        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, "0");
        const day = String(today.getDate()).padStart(2, "0");

        const currentDate = `${year}-${month}-${day}`;

        appointmentDate.min = currentDate;
    }


    // Registration role fields
    const roleSelect = document.querySelector('select[name="role"]');

    const specializationGroup =
        document.getElementById("specialization-group");

    const experienceGroup =
        document.getElementById("experience-group");

    if (roleSelect) {

        function updateRoleFields() {

            if (roleSelect.value === "doctor") {

                if (specializationGroup) {
                    specializationGroup.style.display = "block";
                }

                if (experienceGroup) {
                    experienceGroup.style.display = "block";
                }

            } else {

                if (specializationGroup) {
                    specializationGroup.style.display = "none";
                }

                if (experienceGroup) {
                    experienceGroup.style.display = "none";
                }
            }
        }

        roleSelect.addEventListener("change", updateRoleFields);

        updateRoleFields();
    }


    // Password confirmation
    const password = document.querySelector(
        'input[name="password"]'
    );

    const confirmPassword = document.querySelector(
        'input[name="confirm_password"]'
    );

    if (password && confirmPassword) {

        confirmPassword.addEventListener("input", function () {

            if (password.value !== confirmPassword.value) {
                confirmPassword.setCustomValidity(
                    "Passwords do not match"
                );
            } else {
                confirmPassword.setCustomValidity("");
            }

        });
    }

});
document.addEventListener("DOMContentLoaded", function () {

    /* =========================================
       REGISTER PAGE - ROLE SELECTION
    ========================================= */

    const role = document.getElementById("role");

    const patientFields =
        document.getElementById("patient-fields");

    const doctorFields =
        document.getElementById("doctor-fields");


    if (role && patientFields && doctorFields) {

        function updateRoleFields() {

            if (role.value === "patient") {

                patientFields.style.display = "block";
                doctorFields.style.display = "none";

            }

            else if (role.value === "doctor") {

                patientFields.style.display = "none";
                doctorFields.style.display = "block";

            }

            else {

                patientFields.style.display = "none";
                doctorFields.style.display = "none";

            }

        }

        role.addEventListener("change", updateRoleFields);

        updateRoleFields();
    }


    /* =========================================
       BOOK APPOINTMENT - PREVENT PAST DATES
    ========================================= */

    const appointmentDate =
        document.getElementById("appointment_date");


    if (appointmentDate) {

        const today =
            new Date().toISOString().split("T")[0];

        appointmentDate.min = today;
    }


    /* =========================================
       CONFIRM ACTION
    ========================================= */

    const confirmButtons =
        document.querySelectorAll(".confirm-action");


    confirmButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const confirmed =
                confirm("Are you sure you want to confirm this appointment?");

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });


    /* =========================================
       CANCEL ACTION
    ========================================= */

    const cancelButtons =
        document.querySelectorAll(".cancel-action");


    cancelButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const confirmed =
                confirm("Are you sure you want to cancel this appointment?");

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });


    /* =========================================
       COMPLETE ACTION
    ========================================= */

    const completeButtons =
        document.querySelectorAll(".complete-action");


    completeButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const confirmed =
                confirm("Mark this appointment as completed?");

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });

});