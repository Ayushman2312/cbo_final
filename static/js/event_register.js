document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('eventRegistrationForm');
    const attendanceSelect = document.getElementById('attendanceSelect');
    const additionalAttendees = document.getElementById('additionalAttendees');
    const transportDetails = document.getElementById('transportDetails');
    const numberOfPeople = document.getElementById('numberOfPeople');
    const attendeeDetails = document.getElementById('attendeeDetails');
    const progressBar = document.getElementById('progressBar');
    const registrarDocument = document.getElementById('registrarDocument');
    const eventRegistrarDocument = document.getElementById('eventRegistrarDocument');

    // Handle attendance selection
    attendanceSelect.addEventListener('change', function() {
        if (this.value === 'yes') {
            additionalAttendees.classList.remove('hidden');
            transportDetails.classList.remove('hidden');
            registrarDocument.classList.remove('hidden');
            registrarDocument.setAttribute('tabindex', '0'); // Make focusable
            eventRegistrarDocument.classList.remove('hidden');
            eventRegistrarDocument.setAttribute('tabindex', '0'); // Make focusable
            updateProgress();
        } else {
            additionalAttendees.classList.add('hidden');
            transportDetails.classList.add('hidden');
            registrarDocument.classList.add('hidden');
            registrarDocument.removeAttribute('tabindex');
            eventRegistrarDocument.classList.add('hidden');
            eventRegistrarDocument.removeAttribute('tabindex');
        }
    });

    // Handle number of people change
    numberOfPeople.addEventListener('change', function() {
        attendeeDetails.innerHTML = '';
        for (let i = 0; i < this.value; i++) {
            const attendeeHtml = `
                <div class="space-y-4 p-4 border rounded-md">
                    <h4 class="font-medium text-gray-700">Person ${i + 1}</h4>
                    <input type="text" name="person_${i+1}_name" placeholder="Name" required 
                           class="mt-1 block w-full px-5 py-3 bg-white/70 text-gray-900 rounded-xl border border-gray-200 
                                  placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500
                                  transition-all duration-300 hover:bg-white">
                    <input type="text" name="person_${i+1}_mobile" placeholder="Mobile Number" required 
                           class="mt-1 block w-full px-5 py-3 bg-white/70 text-gray-900 rounded-xl border border-gray-200
                                  placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500
                                  transition-all duration-300 hover:bg-white"
                           pattern="[0-9]{10}"
                           maxlength="10"
                           onkeypress="return event.charCode >= 48 && event.charCode <= 57">
                    <select name="person_${i+1}_id" required 
                            class="mt-1 block w-full px-5 py-3 bg-white/70 text-gray-900 rounded-xl border border-gray-200
                                   placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500
                                   transition-all duration-300 hover:bg-white">
                        <option value="">Select ID Proof</option>
                        <option value="aadhar">Aadhar Card</option>
                        <option value="passport">Passport</option>
                        <option value="license">Driving License</option>
                    </select>
                    <input type="file" name="person_${i+1}_document" accept=".pdf,.jpg,.jpeg,.png" required onchange="validateFile(this)"
                           class="mt-1 block w-full px-5 py-3 bg-white/70 text-gray-900 rounded-xl border border-gray-200
                                  placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500
                                  transition-all duration-300 hover:bg-white">
                </div>
            `;
            attendeeDetails.insertAdjacentHTML('beforeend', attendeeHtml);
        }
        updateProgress();
    });

    // Handle transport mode selection
    ['arrival', 'departure'].forEach(type => {
        const select = document.getElementById(`${type}Transport`);
        const details = document.getElementById(`${type}Details`);

        select.addEventListener('change', function() {
            details.innerHTML = '';
            if (this.value) {
                let fieldsHtml = '';
                switch(this.value) {
                    case 'flight':
                        fieldsHtml = `
                            <input type="text" name="${type}FlightNumber" placeholder="Flight Number" required 
                                   class="mt-1 block w-full px-5 py-3 bg-white/70 text-gray-900 rounded-xl border border-gray-200
                                          placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500
                                          transition-all duration-300 hover:bg-white">
                            <input type="text" name="${type}Terminal" placeholder="Terminal Name" required 
                                   class="mt-4 block w-full px-5 py-3 bg-white/70 text-gray-900 rounded-xl border border-gray-200
                                          placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500
                                          transition-all duration-300 hover:bg-white">
                        `;
                        break;
                    case 'train':
                        fieldsHtml = `
                            <input type="text" name="${type}TrainNumber" placeholder="Train Number" required 
                                   class="mt-1 block w-full px-5 py-3 bg-white/70 text-gray-900 rounded-xl border border-gray-200
                                          placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500
                                          transition-all duration-300 hover:bg-white">
                            <input type="text" name="${type}Station" placeholder="Station Name" required 
                                   class="mt-4 block w-full px-5 py-3 bg-white/70 text-gray-900 rounded-xl border border-gray-200
                                          placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500
                                          transition-all duration-300 hover:bg-white">
                        `;
                        break;
                    case 'bus':
                        fieldsHtml = `
                            <input type="text" name="${type}BusStop" placeholder="Bus Stop" required 
                                   class="mt-1 block w-full px-5 py-3 bg-white/70 text-gray-900 rounded-xl border border-gray-200
                                          placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500
                                          transition-all duration-300 hover:bg-white">
                            <input type="text" name="${type}BusNumber" placeholder="Bus Number (Optional)" 
                                   class="mt-4 block w-full px-5 py-3 bg-white/70 text-gray-900 rounded-xl border border-gray-200
                                          placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500
                                          transition-all duration-300 hover:bg-white">
                        `;
                        break;
                }
                if (fieldsHtml) {
                    fieldsHtml += `
                        <input type="datetime-local" name="${type}DateTime" required 
                               class="mt-4 block w-full px-5 py-3 bg-white/70 text-gray-900 rounded-xl border border-gray-200
                                      placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500
                                      transition-all duration-300 hover:bg-white">
                    `;
                }
                details.innerHTML = fieldsHtml;
            }
            updateProgress();
        });
    });

    // Update progress bar
    function updateProgress() {
        const totalFields = form.querySelectorAll('input:not([type="hidden"]), select, textarea').length;
        const filledFields = form.querySelectorAll('input:not([type="hidden"]):valid, select:valid, textarea:valid').length;
        const progress = (filledFields / totalFields) * 100;
        progressBar.style.width = `${progress}%`;
    }

    // Add input event listeners for real-time validation
    form.querySelectorAll('input, select, textarea').forEach(element => {
        element.addEventListener('input', updateProgress);
        // Make all form controls focusable
        if (!element.hasAttribute('tabindex')) {
            element.setAttribute('tabindex', '0');
        }
    });

    // Form validation and submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (form.checkValidity()) {
            try {
                // Get form data
                const formData = new FormData(form);
                
                // Send POST request to server
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                });

                if (response.ok) {
                    // Successful submission - redirect to home
                    window.location.href = '/thank_you';
                } else {
                    // Handle error response
                    const data = await response.json();
                    if (data.error) {
                        alert(`Error: ${data.error}`);
                        console.error('Server error:', data.error);
                    } else {
                        alert('An error occurred. Please try again.');
                        console.error('Response not OK:', response.status, response.statusText);
                    }
                }

            } catch (error) {
                alert('An error occurred. Please try again.');
                console.error('Error:', error);
                window.location.href = '/register_event'; // Redirect to home on error
            }
        } else {
            window.location.href = '/event_form'; // Redirect to home if form is invalid
        }
    });
});
