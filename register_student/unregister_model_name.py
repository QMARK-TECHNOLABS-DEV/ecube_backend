from django.apps import apps

def unregister_models(model_names):
    for model_name in model_names:
        if model_name in apps.all_models['register_student']:
            print(f'Unregistering model {model_name}')
            model = apps.get_model('register_student', model_name)
            
            if model:
                apps.unregister_model('register_student', model)
            
            
                print(f'Model {model_name} unregistered successfully')

# List of model names to unregister
model_names_to_unregister = [
    'register_student.2021_plustwo_b_exam_results',
    'register_student.2021_plustwo_b_leader_board',
    'register_student.2021_plustwo_b_attendance',
    'register_student.2021_plustwo_b_daily_updates',
    'register_student.2022_plusone_d_exam_results',
    'register_student.2022_plusone_d_leader_board',
    'register_student.2022_plusone_d_attendance',
    'register_student.2022_plusone_d_daily_updates',
    'register_student.2023_classx_c_exam_results',
    'register_student.2023_classx_c_leader_board',
    'register_student.2023_classx_c_attendance',
    'register_student.2023_classx_c_daily_updates',
    'register_student.2023_plusone_a_exam_results',
    'register_student.2023_plusone_a_leader_board',
    'register_student.2023_plusone_a_attendance',
    'register_student.2023_plusone_a_daily_updates',
    
]

# Call the unregister_models function
unregister_models(model_names_to_unregister)