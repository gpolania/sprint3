from ..models import Paciente # Change the model import
import datetime
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO) # Or logging.DEBUG for more detail
BUSINESS_HOUR_START = datetime.time(7, 0, 0)
BUSINESS_HOUR_END = datetime.time(17, 0, 0)
BUSINESS_DAYS = [0, 1, 2, 3, 4] # Lunes=0, Domingo=6

def is_outside_business_hours():
    """Checks if the current time is outside defined business hours/days."""
    now = datetime.datetime.now()
    current_time = now.time()
    current_day_of_week = now.weekday()

    # Check if it's a business day
    if current_day_of_week not in BUSINESS_DAYS:
        # logger.info(f"Access on weekend (Day: {current_day_of_week}) - considered outside business hours.")
        return True
    # Check if it's within business hours on a business day
    if not (BUSINESS_HOUR_START <= current_time < BUSINESS_HOUR_END):
        # logger.info(f"Access on business day (Day: {current_day_of_week}, Time: {current_time}) but outside range {BUSINESS_HOUR_START}-{BUSINESS_HOUR_END}.")
        return True
    # logger.info(f"Access within business hours (Day: {current_day_of_week}, Time: {current_time}).")
    return False

# --- Basic SQL Injection Keyword Check (Copied from Variable code) ---
def contains_sql_injection_keywords(input_value):
    """
    Checks if input_value (string, list, or tuple) contains common SQL injection keywords.
    This is a basic check and should not replace ORM safety or proper input validation.
    """
    sql_keywords = ['DELETE', 'INSERT', 'UPDATE', ';', 'DROP', 'TABLE', 'FROM', 'SELECT', 'UNION', 'EXEC', '--', '#'] # Expanded list
    strings_to_check = []

    if isinstance(input_value, str):
        strings_to_check.append(input_value)
    elif isinstance(input_value, (list, tuple)):
        for item in input_value:
             # Convert items to string for checking, handle None
            strings_to_check.append(str(item) if item is not None else "")
    # Handle other types by converting to string as well if needed, or ignore
    # elif input_value is not None:
    #     strings_to_check.append(str(input_value))


    if not strings_to_check:
        return False

    for text_to_check in strings_to_check:
        # Ensure it's a string and not None
        if not isinstance(text_to_check, str):
             text_to_check = str(text_to_check) # Attempt conversion for other types

        text_to_check_upper = text_to_check.upper()
        for keyword in sql_keywords:
            if keyword in text_to_check_upper:
                # logger.debug(f"SQL keyword '{keyword}' found in '{text_to_check_upper}'")
                return True
    return False

# --- Adapted Paciente Functions ---

def get_pacientes():
    """
    Retrieves all Paciente objects.
    Includes logging for access attempts, especially outside business hours.
    No direct user input parameter, so less susceptible to injection via function args.
    """
    current_call_outside_hours = is_outside_business_hours()

    if current_call_outside_hours:
        logger.info("Attempted access to get_pacientes outside business hours.")
        # Decide here if you want to restrict access outside hours.
        # For now, we'll just log and allow access, as it's generally a read operation.
        # If you wanted to restrict: return Paciente.objects.none() or raise exception

    try:
        queryset = Paciente.objects.all()
        # logger.debug(f"Successfully retrieved {queryset.count()} pacientes.")
        return queryset
    except Exception as e:
        logger.error(f"Error retrieving all pacientes: {e}")
        return Paciente.objects.none() # Return empty queryset on error


def get_paciente(id_param):
    """
    Retrieves a single Paciente by ID.
    Includes business hours check, basic SQL injection keyword check,
    input cleaning, and robust error handling using the ORM.
    """
    id_str = str(id_param) # Ensure input is treated as string initially
    current_call_outside_hours = is_outside_business_hours()

    if current_call_outside_hours:
        logger.info(f"Attempted access to get_paciente outside business hours. ID provided: '{id_str}'")

        # Basic check for suspicious keywords in the input string when outside hours
        if contains_sql_injection_keywords(id_str):
            logger.warning(f"POSSIBLE INJECTION ATTEMPT: SQL keywords detected in get_paciente ID outside business hours. ID: '{id_str}'")
            print("POSSIBLE INJECTION ATTEMPT DETECTED") # User-facing message (for development/debugging)
            return None # Reject the request

    # --- Input Cleaning and Validation ---
    cleaned_id = None
    try:
        # Attempt to convert the input to an integer (assuming PK is integer)
        # We still do this even with ORM's pk= check, as it validates input type early.
        cleaned_id = int(id_str.split(';')[0]) # Take only the part before first ';'
    except ValueError:
        # This error occurs if the input isn't a valid integer
        log_message = f"MALFORMED ID (NOT NUMERIC): ID '{id_str}' is not a valid number for get_paciente."
        if current_call_outside_hours:
             logger.warning(f"POSSIBLE INJECTION ATTEMPT: {log_message} (Outside Business Hours)")
             print("POSSIBLE INJECTION ATTEMPT DETECTED")
        else:
             logger.warning(log_message)
        return None
    except Exception as e:
         # Catch any other unexpected errors during cleaning
         log_message = f"UNEXPECTED ERROR cleaning ID '{id_str}' for get_paciente: {e}"
         if current_call_outside_hours:
             logger.error(f"POSSIBLE INJECTION ATTEMPT: {log_message} (Outside Business Hours)")
             print("POSSIBLE INJECTION ATTEMPT DETECTED")
         else:
             logger.error(log_message)
         return None

    # --- ORM Lookup (Safely using cleaned ID) ---
    try:
        # Use the Django ORM's get method with the primary key (pk)
        # This is safer than raw SQL string formatting as ORM handles parameterization.
        paciente = Paciente.objects.get(pk=cleaned_id)
        # logger.debug(f"Successfully retrieved paciente with ID: {cleaned_id}")
        return paciente
    except Paciente.DoesNotExist:
        # logger.info(f"Paciente with ID {cleaned_id} not found.")
        return None # Return None if the object doesn't exist
    except Exception as e:
        # Catch any other database or ORM errors
        logger.error(f"Database error retrieving paciente with ID {cleaned_id}: {e}")
        return None


def create_paciente(form):
    """
    Creates a new Paciente object using a ModelForm.
    Includes business hours check, basic SQL injection keyword check on form data,
    form validation, and error handling.
    """
    current_call_outside_hours = is_outside_business_hours()
    all_form_values = []

    # Collect all values from the form data for checking
    if hasattr(form, 'data'):
        for key in form.data:
            # Use getlist to handle potential multi-value fields (like checkboxes)
            all_form_values.extend(form.data.getlist(key))

    if current_call_outside_hours:
        # Log a preview of the form data when outside business hours
        log_data_preview = {k: form.data.getlist(k) for k in form.data.keys()}
        logger.info(f"Attempted access to create_paciente outside business hours. Data (preview): '{log_data_preview}'")

    # Basic check for suspicious keywords in form data when outside hours
    if current_call_outside_hours and contains_sql_injection_keywords(all_form_values):
        log_data_full = {k: form.data.getlist(k) for k in form.data.keys()} # Log full data on detection
        logger.warning(f"POSSIBLE INJECTION ATTEMPT: SQL keywords detected in create_paciente form data outside business hours. Data: '{log_data_full}'")
        print("POSSIBLE INJECTION ATTEMPT DETECTED")
        return None # Reject the request

    # --- Form Validation and Saving ---
    if form.is_valid():
        try:
            # form.save() creates and saves the new object using the ORM
            paciente = form.save()
            # logger.info(f"Successfully created new paciente with ID: {paciente.pk}")
            return paciente # Return the newly created object
        except Exception as e:
            logger.error(f"Error saving new paciente from form: {e}")
            return None # Return None on database error
    else:
        # Log form validation errors
        # logger.warning(f"Invalid form data for create_paciente. Errors: {form.errors.as_json()}")
        # print("Form validation failed.") # Optional: Print to console during development
        return None # Return None if the form is invalid


def update_paciente(paciente, form):
    """
    Updates an existing Paciente object using a ModelForm bound to the instance.
    Includes business hours check, basic SQL injection keyword check on form data,
    form validation, and error handling.
    Assumes the form is already instantiated with `instance=paciente`.
    """
    current_call_outside_hours = is_outside_business_hours()
    all_form_values = []

    # Collect all values from the form data for checking
    if hasattr(form, 'data'):
        for key in form.data:
            all_form_values.extend(form.data.getlist(key))

    if current_call_outside_hours:
        # Log a preview of the form data when outside business hours
        log_data_preview = {k: form.data.getlist(k) for k in form.data.keys()}
        logger.info(f"Attempted access to update_paciente outside business hours for ID {paciente.pk}. Data (preview): '{log_data_preview}'")

    # Basic check for suspicious keywords in form data when outside hours
    if current_call_outside_hours and contains_sql_injection_keywords(all_form_values):
        log_data_full = {k: form.data.getlist(k) for k in form.data.keys()} # Log full data on detection
        logger.warning(f"POSSIBLE INJECTION ATTEMPT: SQL keywords detected in update_paciente form data outside business hours for ID {paciente.pk}. Data: '{log_data_full}'")
        print("POSSIBLE INJECTION ATTEMPT DETECTED")
        return None # Reject the request

    # --- Form Validation and Saving ---
    if form.is_valid():
        try:
            # form.save() updates the bound instance using the ORM
            updated_paciente = form.save()
            # logger.info(f"Successfully updated paciente with ID: {updated_paciente.pk}")
            return updated_paciente # Return the updated object
        except Exception as e:
            logger.error(f"Error saving updated paciente from form for ID {paciente.pk}: {e}")
            return None # Return None on database error
    else:
        # Log form validation errors
        # logger.warning(f"Invalid form data for update_paciente for ID {paciente.pk}. Errors: {form.errors.as_json()}")
        # print("Form validation failed.") # Optional: Print to console during development
        return None # Return None if the form is invalid
