from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import *
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.urls import reverse
import json


def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)  # Use objects.get instead of GetUserByEmail
            check = check_password(password, user.password)
            if check:
                request.session['email'] = email
                return redirect('dashboard')
            else:
                messages.info(request, "Invalid Password or Username")
                return render(request, 'home.html', {'error': "Invalid Password or Username"})
        except User.DoesNotExist:
            messages.info(request, "Username does not exist")
            return render(request, 'home.html', {'error': "Username does not exist"})
    return render(request, 'home.html')

def signup(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if User.objects.filter(email=email).exists():
            messages.info(request, "Email already exists")
            return render(request, 'signup.html', {'error': "Email already exists"})

        if password != confirm_password:
            messages.info(request, "Passwords do not match")
            return render(request, 'signup.html', {'error': "Passwords do not match"})

        user = User(
            email=email,
            password=make_password(password)  # Hash the password before saving
        )
        user.save()
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('login')

    return render(request, 'signup.html')

def logout(request):
    request.session.clear()
    return redirect('dashboard')

#my code 

class Dashboard(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = Events.objects.all()
        print("Retrieved Events:", events)
        context['events'] = events
        return context
    
class CreateEventView(TemplateView):
    template_name = "create_event.html"

    def post(self, request, *args, **kwargs):
        event_image = request.FILES.get('event_image')
        event_name = request.POST.get('event_name')
        event_venue = request.POST.get('event_venue')
        event_date = request.POST.get('event_date')
        event_description = request.POST.get('event_description')

        k = Events.objects.create(
            event_image=event_image,
            event_name=event_name,
            event_venue=event_venue,
            event_date=event_date,
            event_description=event_description
        )
        k.save()
        return redirect('dashboard')
        return render(request, 'dashboard.html', {'success': True})
    
class EditEventView(TemplateView):
    template_name = "edit_event.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_name = kwargs['event_name']
        try:
            event = Events.objects.get(event_name=event_name)
            context['event'] = event
        except Events.DoesNotExist:
            context['event'] = None
        except Events.MultipleObjectsReturned:
            context['event'] = Events.objects.filter(event_name=event_name).first()
        return context

    def post(self, request, *args, **kwargs):
        event_name = kwargs['event_name']
        try:
            event = Events.objects.get(event_name=event_name)
            event_name = request.POST.get('event_name')
            event_venue = request.POST.get('event_venue')
            event_date = request.POST.get('event_date')
            event_description = request.POST.get('event_description')

            event.event_name = event_name
            event.event_venue = event_venue
            event.event_date = event_date
            event.event_description = event_description

            event.save()

            return redirect('dashboard')
            return render(request, self.template_name, {'success': True})
        except Events.DoesNotExist:
            return render(request, self.template_name, {'success': False, 'error': 'Event not found'})


class DeleteEventView(TemplateView):
    def get(self, request, *args, **kwargs):
        event_name = kwargs['event_name']
        try:
            # Get single event with exact matching name and delete it
            event = Events.objects.get(event_name=event_name)
            event.delete()
            return redirect('dashboard')
        except Events.DoesNotExist:
            # Event not found, redirect back
            return redirect('dashboard')
        except Exception:
            # Handle any other errors
            return redirect('dashboard')
    

    
class EventRegistrationView(TemplateView):
    template_name = "event_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_name = kwargs.get('event_name')
        try:
            event = Events.objects.get(event_name=event_name)
            context['event'] = event
            # Add the event name to the context for use in form action URL
            context['event_name'] = event_name
        except Events.DoesNotExist:
            context['event'] = None
        return context

    def post(self, request, *args, **kwargs):
        event_name = kwargs.get('event_name')
        try:
            event = Events.objects.get(event_name=event_name)
            
            # Get form data with default values to prevent None errors
            name = request.POST.get('name', '')
            email = request.POST.get('email', '')
            country_code = request.POST.get('country_code', '')
            mobile = request.POST.get('mobile', '')
            attending = request.POST.get('attendance') == 'yes'
            remarks = request.POST.get('remarks', '')
            
            try:
                num_attendees = int(request.POST.get('numberOfPeople', '0'))
            except (ValueError, TypeError):
                num_attendees = 0

            # Create registration record with error handling for file upload
            registration_data = {
                'event': event,
                'name': name,
                'email': email,
                'country_code': country_code,
                'mobile_number': mobile,
                'flag_attending': 'yes' if attending else 'no',
                'remarks': remarks,
                'number_of_people': num_attendees
            }

            if 'registrar_document' in request.FILES:
                registration_data['registrar_document'] = request.FILES['registrar_document']

            registration = EventRegistration.objects.create(**registration_data)

            # Add attendees if attending
            if attending and num_attendees > 0:
                for i in range(num_attendees):
                    attendee_data = {
                        'registration': registration,
                        'name': request.POST.get(f'person_{i+1}_name', ''),
                        'mobile_number': request.POST.get(f'person_{i+1}_mobile', ''),
                        'identification_proof': request.POST.get(f'person_{i+1}_id', '')
                    }

                    # Handle attendee document upload
                    doc_key = f'person_{i+1}_document'
                    if doc_key in request.FILES:
                        attendee_data['registrar_document'] = request.FILES[doc_key]

                    Attendee.objects.create(**attendee_data)

                # Handle arrival transport with validation
                arrival_mode = request.POST.get('arrivalTransport')
                if arrival_mode:
                    arrival_data = {
                        'registration': registration,
                        'mode_of_transport': arrival_mode,
                        'flight_number': request.POST.get('arrivalFlightNumber', ''),
                        'terminal_name': request.POST.get('arrivalTerminal', ''),
                        'train_number': request.POST.get('arrivalTrainNumber', ''),
                        'train_arrival_station': request.POST.get('arrivalStation', ''),
                        'bus_number': request.POST.get('arrivalBusNumber', ''),
                        'bus_stop': request.POST.get('arrivalBusStop', ''),
                        'arrival_date': request.POST.get('arrivalDateTime', None)
                    }
                    TransportDetails.objects.create(**{k: v for k, v in arrival_data.items() if v})

                # Handle departure transport with validation
                departure_mode = request.POST.get('departureTransport')
                if departure_mode:
                    departure_data = {
                        'registration': registration,
                        'mode_of_transport': departure_mode,
                        'flight_number': request.POST.get('departureFlightNumber', ''),
                        'terminal_name': request.POST.get('departureTerminal', ''),
                        'train_number': request.POST.get('departureTrainNumber', ''),
                        'train_arrival_station': request.POST.get('departureStation', ''),
                        'bus_number': request.POST.get('departureBusNumber', ''),
                        'bus_stop': request.POST.get('departureBusStop', ''),
                        'departure_date': request.POST.get('departureDateTime', None)
                    }
                    TransportDetails.objects.create(**{k: v for k, v in departure_data.items() if v})

            # Set session variables for thank you page
            request.session['form_submitted'] = True
            request.session['event_name'] = event_name

            return redirect('thank_you')

        except Events.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Event not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class EventEntriesView(TemplateView):
    template_name = 'event_entries.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_name = kwargs.get('event_name')
        
        try:
            # Get the event
            event = Events.objects.get(event_name=event_name)
            context['event'] = event

            # Get all registrations for this event
            registrations = EventRegistration.objects.filter(event=event)
            
            entries = []
            for registration in registrations:
                # Fetch transport details for both arrival and departure
                arrival_transport = TransportDetails.objects.filter(
                    registration=registration, 
                    departure_date__isnull=True
                ).first()
                
                departure_transport = TransportDetails.objects.filter(
                    registration=registration,
                    arrival_date__isnull=True
                ).first()
                
                transport_details = {
                    'arrival': arrival_transport,
                    'departure': departure_transport
                }
                
                # Fetch and format attendee details
                attendees = Attendee.objects.filter(registration=registration)
                attendee_details = []
                for attendee in attendees:
                    attendee_details.append({
                        'name': attendee.name,
                        'mobile_number': attendee.mobile_number,
                        'identification_proof': attendee.identification_proof,
                        'registrar_document': attendee.registrar_document.url if attendee.registrar_document else None  # Include document URL
                    })
                
                # Add attendee details directly to registration object
                registration.attendee_details = attendee_details
                
                entry = {
                    'registration': registration,
                    'attendees': attendees,
                    'transport_details': transport_details
                }
                entries.append(entry)

            context['entries'] = entries
            return context

        except Events.DoesNotExist:
            context['error'] = 'Event not found'
            return context


    def post(self, request, *args, **kwargs):
        event_name = kwargs.get('event_name')
        registration_id = kwargs.get('registration_id')

        try:
            event = Events.objects.get(event_name=event_name)
            registration = EventRegistration.objects.get(id=registration_id, event=event)

            # Update registration details
            registration.name = request.POST.get('name')
            registration.country_code = request.POST.get('countryCode')
            registration.mobile_number = request.POST.get('mobileNumber')
            registration.email = request.POST.get('email')
            registration.flag_attending = request.POST.get('flagAttending')
            registration.number_of_people = int(request.POST.get('numberOfPeople', 0))
            registration.remarks = request.POST.get('remarks')
            registration.arrival_transport = request.POST.get('arrivalTransport')
            registration.departure_transport = request.POST.get('departureTransport')
            registration.save()

            # Update attendees
            existing_attendees = Attendee.objects.filter(registration=registration)
            existing_attendees.delete()  # Remove existing attendees

            # Create new attendees based on number_of_people
            if registration.flag_attending == 'yes' and registration.number_of_people > 0:
                for i in range(registration.number_of_people):
                    Attendee.objects.create(
                        registration=registration,
                        name=request.POST.get(f'person_{i+1}_name'),
                        mobile_number=request.POST.get(f'person_{i+1}_mobile'),
                        identification_proof=request.POST.get(f'person_{i+1}_id')
                    )

            # Update transport details
            # Delete existing transport details first
            TransportDetails.objects.filter(registration=registration).delete()

            # Create new arrival transport details if specified
            if registration.arrival_transport:
                arrival_details = {
                    'flight_number': request.POST.get('arrivalFlightNumber'),
                    'terminal_name': request.POST.get('arrivalTerminal'),
                    'train_number': request.POST.get('arrivalTrainNumber'),
                    'train_arrival_station': request.POST.get('arrivalStation'),
                    'bus_number': request.POST.get('arrivalBusNumber'),
                    'bus_stop': request.POST.get('arrivalBusStop'),
                    'arrival_date': request.POST.get('arrivalDateTime')
                }
                TransportDetails.objects.create(
                    registration=registration,
                    mode_of_transport=registration.arrival_transport,
                    **{k: v for k, v in arrival_details.items() if v}  # Only include non-empty values
                )

            # Create new departure transport details if specified
            if registration.departure_transport:
                departure_details = {
                    'flight_number': request.POST.get('departureFlightNumber'),
                    'terminal_name': request.POST.get('departureTerminal'),
                    'train_number': request.POST.get('departureTrainNumber'),
                    'train_arrival_station': request.POST.get('departureStation'),
                    'bus_number': request.POST.get('departureBusNumber'),
                    'bus_stop': request.POST.get('departureBusStop'),
                    'departure_date': request.POST.get('departureDateTime')
                }
                TransportDetails.objects.create(
                    registration=registration,
                    mode_of_transport=registration.departure_transport,
                    **{k: v for k, v in departure_details.items() if v}  # Only include non-empty values
                )

            return redirect('view_entries', event_name=event_name)

        except (Events.DoesNotExist, EventRegistration.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Entry not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class ThankYouView(TemplateView):
    template_name = 'thank_you.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.session.get('form_submitted'):
            # If form wasn't submitted, user shouldn't access this page
            context['error'] = 'Please submit a registration form first'
        else:
            # Clear the session after showing thank you page
            event_name = self.request.session.get('event_name')
            context['event_name'] = event_name
            self.request.session.pop('form_submitted', None)
            self.request.session.pop('event_name', None)
        return context
    
class EditEntryView(TemplateView):
    template_name = "edit_entry.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_name = kwargs.get('event_name')
        registration_id = kwargs.get('registration_id')

        try:
            event = Events.objects.get(event_name=event_name)
            registration = EventRegistration.objects.get(id=registration_id, event=event)
            
            # Get attendees
            attendees = Attendee.objects.filter(registration=registration)
            
            # Get transport details
            arrival_transport = TransportDetails.objects.filter(
                registration=registration,
                mode_of_transport='arrival'
            ).first()
            departure_transport = TransportDetails.objects.filter(
                registration=registration, 
                mode_of_transport='departure'
            ).first()

            context.update({
                'event': event,
                'registration': registration,
                'attendees': attendees,
                'arrival_transport': arrival_transport,
                'departure_transport': departure_transport
            })

        except (Events.DoesNotExist, EventRegistration.DoesNotExist):
            context['error'] = 'Registration not found'

        return context

    def post(self, request, *args, **kwargs):
        event_name = kwargs.get('event_name')
        registration_id = kwargs.get('registration_id')

        try:
            event = Events.objects.get(event_name=event_name)
            registration = EventRegistration.objects.get(id=registration_id, event=event)

            # Update registration details
            registration.name = request.POST.get('name')
            registration.country_code = request.POST.get('country_code')
            registration.mobile_number = request.POST.get('mobile')
            registration.flag_attending = 'yes' if request.POST.get('attendance') == 'yes' else 'no'
            registration.remarks = request.POST.get('remarks')
            registration.number_of_people = int(request.POST.get('numberOfPeople', 0))

            if request.FILES.get('registrar_document'):
                registration.registrar_document = request.FILES.get('registrar_document')

            registration.save()

            # Handle attendees
            if registration.flag_attending == 'yes':
                # Delete existing attendees
                Attendee.objects.filter(registration=registration).delete()
                
                # Create new attendees
                for i in range(registration.number_of_people):
                    attendee_data = {
                        'registration': registration,
                        'name': request.POST.get(f'person_{i+1}_name'),
                        'mobile_number': request.POST.get(f'person_{i+1}_mobile'),
                        'identification_proof': request.POST.get(f'person_{i+1}_id')
                    }
                    
                    if request.FILES.get(f'person_{i+1}_document'):
                        attendee_data['registrar_document'] = request.FILES.get(f'person_{i+1}_document')
                        
                    Attendee.objects.create(**attendee_data)

            # Handle transport details
            TransportDetails.objects.filter(registration=registration).delete()

            # Create new arrival transport details if specified
            if registration.arrival_transport:
                arrival_details = {
                    'flight_number': request.POST.get('arrivalFlightNumber'),
                    'terminal_name': request.POST.get('arrivalTerminal'),
                    'train_number': request.POST.get('arrivalTrainNumber'),
                    'train_arrival_station': request.POST.get('arrivalStation'),
                    'bus_number': request.POST.get('arrivalBusNumber'),
                    'bus_stop': request.POST.get('arrivalBusStop'),
                    'arrival_date': request.POST.get('arrivalDateTime')
                }
                TransportDetails.objects.create(
                    registration=registration,
                    mode_of_transport=registration.arrival_transport,
                    **{k: v for k, v in arrival_details.items() if v}
                )

            # Create new departure transport details if specified
            if registration.departure_transport:
                departure_details = {
                    'flight_number': request.POST.get('departureFlightNumber'),
                    'terminal_name': request.POST.get('departureTerminal'),
                    'train_number': request.POST.get('departureTrainNumber'),
                    'train_arrival_station': request.POST.get('departureStation'),
                    'bus_number': request.POST.get('departureBusNumber'),
                    'bus_stop': request.POST.get('departureBusStop'),
                    'departure_date': request.POST.get('departureDateTime')
                }
                TransportDetails.objects.create(
                    registration=registration,
                    mode_of_transport=registration.departure_transport,
                    **{k: v for k, v in departure_details.items() if v}
                )

            return redirect('view_entries', event_name=event_name)

        except (Events.DoesNotExist, EventRegistration.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Entry not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)



# class DeleteEntryView(TemplateView):
#     template_name = 'event_entries.html'

#     def post(self, request, event_name, registration_id):
#         try:
#             # Get the event and registration
#             event = Events.objects.get(event_name=event_name)
#             registration = EventRegistration.objects.get(id=registration_id, event=event)

#             # Delete the registration (this will cascade delete related attendees and transport details)
#             registration.delete()

#             return redirect('view_entries', event_name=event_name)

#         except Events.DoesNotExist:
#             context = {'error': 'Event not found'}
#             return self.render_to_response(context, status=404)
#         except EventRegistration.DoesNotExist:
#             context = {'error': 'Registration not found'}
#             return self.render_to_response(context, status=404)
#         except Exception as e:
#             context = {'error': str(e)}
#             return self.render_to_response(context, status=400)
