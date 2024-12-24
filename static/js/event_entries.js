document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const sortOrder = document.getElementById('sortOrder');
    const tableBody = document.getElementById('entriesTableBody');

    // Store original rows for resetting
    let originalRows = Array.from(tableBody.getElementsByTagName('tr'));

    function filterAndSortEntries() {
        // Reset to original rows before filtering
        let rows = [...originalRows];
        const searchTerm = searchInput.value.toLowerCase();
        const sortValue = sortOrder.value;

        // Filter rows based on search term in the name
        const filteredRows = rows.filter(row => {
            // Skip the "No entries found" row
            if (row.cells.length === 1 && row.cells[0].textContent.includes('No entries found')) {
                return false;
            }

            // If search term is empty, show all rows
            if (!searchTerm) {
                return true;
            }

            // Get text content from all cells in the row
            const rowText = Array.from(row.cells).map(cell => cell.textContent.toLowerCase()).join(' ');
            return rowText.includes(searchTerm);
        });

        // Sort rows based on selected order
        filteredRows.sort((a, b) => {
            const nameA = a.cells[0]?.textContent.toLowerCase() || '';
            const nameB = b.cells[0]?.textContent.toLowerCase() || '';
            const dateA = new Date(a.getAttribute('data-registration-date') || 0);
            const dateB = new Date(b.getAttribute('data-registration-date') || 0);

            switch(sortValue) {
                case 'name_asc':
                    return nameA.localeCompare(nameB);
                case 'name_desc':
                    return nameB.localeCompare(nameA);
                case 'date_newest':
                    return dateB.getTime() - dateA.getTime();
                case 'date_oldest':
                    return dateA.getTime() - dateB.getTime();
                default:
                    return 0;
            }
        });

        // Clear and repopulate table
        while (tableBody.firstChild) {
            tableBody.removeChild(tableBody.firstChild);
        }

        // If no results found, show message
        if (filteredRows.length === 0) {
            const noResultsRow = document.createElement('tr');
            noResultsRow.innerHTML = `
                <td colspan="6" class="px-6 py-8 text-center">
                    <i class="fas fa-search text-4xl text-gray-500 mb-4"></i>
                    <p class="text-gray-400">No matching records found</p>
                </td>`;
            tableBody.appendChild(noResultsRow);
        } else {
            filteredRows.forEach(row => tableBody.appendChild(row));
        }
    }

    // Add debounce to search input to improve performance
    let searchTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(filterAndSortEntries, 300);
    });
    
    sortOrder.addEventListener('change', filterAndSortEntries);

    // Popup functionality for attendees
    const attendeesPopup = document.getElementById('attendeesPopup');
    const attendeesPopupContent = attendeesPopup.querySelector('.bg-gray-800');
    const closeAttendeesPopup = document.getElementById('closePopup');
    
    // Function to open attendees popup
    window.openAttendeesPopup = function(element) {
        const rawData = element.dataset.attendees;
        
        let attendeesData;
        try {
            // Parse the raw data, handling both array and object formats
            attendeesData = JSON.parse(rawData.replace(/&quot;/g, '"')
                                            .replace(/\u0027/g, '"')
                                            .replace(/None/g, 'null')
                                            .replace(/'/g, '"'));

            // Convert to array if object
            if (!Array.isArray(attendeesData)) {
                attendeesData = [attendeesData];
            }
        } catch (e) {
            console.error('Error parsing attendees data:', e, rawData);
            const attendeesList = document.getElementById('attendeesList');
            attendeesList.innerHTML = '<p class="text-gray-400">Error loading attendee details</p>';
            return;
        }

        const attendeesList = document.getElementById('attendeesList');
        attendeesList.innerHTML = '';
        
        if (!attendeesData || attendeesData.length === 0) {
            attendeesList.innerHTML = '<p class="text-gray-400">No attendee details available</p>';
        } else {
            let html = '';
            attendeesData.forEach((attendee, index) => {
                html += `
                    <div class="mb-3 p-3 bg-gray-700/50 rounded-lg">
                        <p class="font-semibold text-white">${attendee.name || 'No name provided'}</p>
                        <p class="text-sm text-gray-400">Mobile: ${attendee.mobile_number || attendee.mobile || 'Not provided'}</p>
                        <p class="text-sm text-gray-400">ID: ${attendee.identification_proof || attendee.id_proof || 'Not provided'}</p>
                    </div>
                `;
            });
            attendeesList.innerHTML = html;
        }
        
        attendeesPopup.classList.remove('hidden');
        attendeesPopup.classList.add('flex');
        setTimeout(() => {
            attendeesPopupContent.classList.remove('scale-0', 'opacity-0');
            attendeesPopupContent.classList.add('scale-100', 'opacity-100');
        }, 50);
    };

    // Transport Details Popup
    const transportPopupHTML = `
        <div id="transportPopup" class="fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50">
            <div class="bg-gray-800 border border-gray-700 rounded-xl p-6 max-w-md w-full mx-4 transform scale-0 opacity-0 transition-all duration-300">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-semibold text-white">Transport Details</h3>
                    <button class="text-gray-400 hover:text-white" id="closeTransportPopup">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div id="transportDetails" class="text-gray-300">
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', transportPopupHTML);

    const transportPopup = document.getElementById('transportPopup');
    const transportPopupContent = transportPopup.querySelector('.bg-gray-800');

    // Function to open transport details popup
    window.openTransportPopup = function(element) {
        let transportData;
        try {
            // Clean and normalize the data string
            let rawTransport = element.dataset.transport
                .replace(/&quot;/g, '"')
                .replace(/\u0027/g, '"')
                .replace(/None/g, 'null')
                .replace(/'/g, '"'); // Replace any remaining single quotes
            
            // Ensure the string is valid JSON
            if (!rawTransport.startsWith('{')) {
                throw new Error('Invalid JSON format');
            }
            
            transportData = JSON.parse(rawTransport);
        } catch (e) {
            console.error('Error parsing transport data:', e);
            const transportDetailsDiv = document.getElementById('transportDetails');
            transportDetailsDiv.innerHTML = '<p class="text-gray-400">No transport details available</p>';
            return;
        }

        const transportDetailsDiv = document.getElementById('transportDetails');
        
        let html = '';
        if (transportData && (transportData.arrival || transportData.departure)) {
            if (transportData.arrival && transportData.arrival !== null) {
                html += `
                    <div class="mb-4 p-3 bg-gray-700/50 rounded-lg">
                        <h4 class="font-semibold text-white mb-2">Arrival Details</h4>
                        <p class="text-gray-300">Mode: ${transportData.arrival.mode_of_transport || 'Not provided'}</p>
                        <p class="text-gray-300">Date: ${transportData.arrival.arrival_date || 'Not provided'}</p>
                        ${transportData.arrival.flight_number ? `<p class="text-gray-300">Flight: ${transportData.arrival.flight_number}</p>` : ''}
                        ${transportData.arrival.train_number ? `<p class="text-gray-300">Train: ${transportData.arrival.train_number}</p>` : ''}
                        ${transportData.arrival.bus_number ? `<p class="text-gray-300">Bus: ${transportData.arrival.bus_number}</p>` : ''}
                    </div>
                `;
            }
            
            if (transportData.departure && transportData.departure !== null) {
                html += `
                    <div class="p-3 bg-gray-700/50 rounded-lg">
                        <h4 class="font-semibold text-white mb-2">Departure Details</h4>
                        <p class="text-gray-300">Mode: ${transportData.departure.mode_of_transport || 'Not provided'}</p>
                        <p class="text-gray-300">Date: ${transportData.departure.departure_date || 'Not provided'}</p>
                        ${transportData.departure.flight_number ? `<p class="text-gray-300">Flight: ${transportData.departure.flight_number}</p>` : ''}
                        ${transportData.departure.train_number ? `<p class="text-gray-300">Train: ${transportData.departure.train_number}</p>` : ''}
                        ${transportData.departure.bus_number ? `<p class="text-gray-300">Bus: ${transportData.departure.bus_number}</p>` : ''}
                    </div>
                `;
            }
        }

        transportDetailsDiv.innerHTML = html || '<p class="text-gray-400">No transport details available</p>';
        
        transportPopup.classList.remove('hidden');
        transportPopup.classList.add('flex');
        setTimeout(() => {
            transportPopupContent.classList.remove('scale-0', 'opacity-0');
            transportPopupContent.classList.add('scale-100', 'opacity-100');
        }, 50);
    };

    // Close popup handlers
    function closePopupHandler(popup, popupContent) {
        popupContent.classList.remove('scale-100', 'opacity-100');
        popupContent.classList.add('scale-0', 'opacity-0');
        setTimeout(() => {
            popup.classList.remove('flex');
            popup.classList.add('hidden');
        }, 300);
    }
    
    closeAttendeesPopup.addEventListener('click', () => closePopupHandler(attendeesPopup, attendeesPopupContent));
    attendeesPopup.addEventListener('click', (e) => {
        if (e.target === attendeesPopup) {
            closePopupHandler(attendeesPopup, attendeesPopupContent);
        }
    });

    const closeTransportPopup = document.getElementById('closeTransportPopup');
    closeTransportPopup.addEventListener('click', () => closePopupHandler(transportPopup, transportPopupContent));
    transportPopup.addEventListener('click', (e) => {
        if (e.target === transportPopup) {
            closePopupHandler(transportPopup, transportPopupContent);
        }
    });
});

document.getElementById('sortOrder').addEventListener('change', function() {
    const value = this.value;
    const tableBody = document.getElementById('entriesTableBody');
    const rows = Array.from(tableBody.getElementsByTagName('tr'));

    rows.forEach(row => {
        const attendingCell = row.querySelector('td:nth-child(4)');
        const attendingText = attendingCell.textContent.trim().toLowerCase();
        
        if (value === 'attending_yes') {
            row.style.display = attendingText === 'yes' ? '' : 'none';
        } else if (value === 'attending_no') {
            row.style.display = attendingText === 'no' ? '' : 'none';
        } else {
            row.style.display = '';
        }
    });
});