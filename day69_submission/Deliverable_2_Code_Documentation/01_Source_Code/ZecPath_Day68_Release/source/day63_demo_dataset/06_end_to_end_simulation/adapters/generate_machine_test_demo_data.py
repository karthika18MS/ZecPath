
import json
from pathlib import Path
from datetime import datetime


# ============================================================
# ZecPath Day 63 - Simulated Machine Test Dataset Generator
# CAND001-CAND009: DEMO DATA
# CAND010: NOT PROVIDED
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    BASE_DIR.parent
    / "04_candidate_responses"
    / "machine_test_responses"
)


# ============================================================
# 1. DEMO SUBMISSION DATA
# ============================================================

DEMO_CANDIDATES = [

    {
        "candidate_id": "CAND001",
        "job_id": "JD001",
        "task_id": "MERN_TASK_001",
        "title": "MERN Employee Management API",
        "requirements": [
            "Create employee records",
            "Retrieve employee records",
            "Validate incoming data",
            "Handle API errors"
        ],
        "candidate_code": """
const express = require('express');
const app = express();

app.use(express.json());

let employees = [];

app.post('/employees', (req, res) => {
    const { name, email } = req.body;

    if (!name || !email) {
        return res.status(400).json({
            error: 'Name and email required'
        });
    }

    const employee = {
        id: employees.length + 1,
        name,
        email
    };

    employees.push(employee);
    res.status(201).json(employee);
});

app.get('/employees', (req, res) => {
    res.json(employees);
});

app.listen(3000);
""",
        "passed_tests": 8,
        "review_scores": {
            "requirement_coverage": 90,
            "code_quality": 88,
            "readability": 90
        }
    },

    {
        "candidate_id": "CAND002",
        "job_id": "JD002",
        "task_id": "PYTHON_TASK_002",
        "title": "Python Employee Data Processing",
        "requirements": [
            "Process employee records",
            "Calculate average salary",
            "Filter employee records",
            "Handle empty input"
        ],
        "candidate_code": """
def process_employees(employees):

    if not employees:
        return {
            "employees": [],
            "average_salary": 0
        }

    valid_employees = [
        employee for employee in employees
        if "salary" in employee
    ]

    if not valid_employees:
        return {
            "employees": [],
            "average_salary": 0
        }

    average_salary = (
        sum(item["salary"] for item in valid_employees)
        / len(valid_employees)
    )

    return {
        "employees": valid_employees,
        "average_salary": average_salary
    }
""",
        "passed_tests": 9,
        "review_scores": {
            "requirement_coverage": 88,
            "code_quality": 85,
            "readability": 90
        }
    },

    {
        "candidate_id": "CAND003",
        "job_id": "JD001",
        "task_id": "MERN_TASK_003",
        "title": "React Form Validation",
        "requirements": [
            "Create a React form",
            "Validate required fields",
            "Display validation messages",
            "Handle form submission"
        ],
        "candidate_code": """
import React, { useState } from 'react';

function EmployeeForm() {

    const [name, setName] = useState('');
    const [error, setError] = useState('');

    function handleSubmit(event) {
        event.preventDefault();

        if (!name.trim()) {
            setError('Name is required');
            return;
        }

        setError('');
        console.log('Employee:', name);
    }

    return (
        <form onSubmit={handleSubmit}>
            <input
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="Employee name"
            />

            {error && <p>{error}</p>}

            <button type="submit">Submit</button>
        </form>
    );
}

export default EmployeeForm;
""",
        "passed_tests": 7,
        "review_scores": {
            "requirement_coverage": 80,
            "code_quality": 78,
            "readability": 82
        }
    },

    {
        "candidate_id": "CAND004",
        "job_id": "JD003",
        "task_id": "JAVA_TASK_004",
        "title": "Java Employee Management",
        "requirements": [
            "Create an Employee class",
            "Store employee information",
            "Calculate annual salary",
            "Display employee details"
        ],
        "candidate_code": """
class Employee {

    private String name;
    private double monthlySalary;

    public Employee(String name, double monthlySalary) {
        this.name = name;
        this.monthlySalary = monthlySalary;
    }

    public double calculateAnnualSalary() {
        return monthlySalary * 12;
    }

    public void displayDetails() {
        System.out.println("Name: " + name);
        System.out.println(
            "Annual Salary: " + calculateAnnualSalary()
        );
    }

    public static void main(String[] args) {

        Employee employee = new Employee(
            "Arun",
            25000
        );

        employee.displayDetails();
    }
}
""",
        "passed_tests": 7,
        "review_scores": {
            "requirement_coverage": 78,
            "code_quality": 75,
            "readability": 80
        }
    },

    {
        "candidate_id": "CAND005",
        "job_id": "JD003",
        "task_id": "JAVA_TASK_005",
        "title": "Spring Boot REST Service",
        "requirements": [
            "Create REST endpoints",
            "Implement employee service",
            "Use dependency injection",
            "Handle missing employee records"
        ],
        "candidate_code": """
@Service
class EmployeeService {

    private final EmployeeRepository repository;

    public EmployeeService(EmployeeRepository repository) {
        this.repository = repository;
    }

    public List<Employee> getEmployees() {
        return repository.findAll();
    }

    public Optional<Employee> getEmployee(Long id) {
        return repository.findById(id);
    }
}

@RestController
@RequestMapping("/employees")
class EmployeeController {

    private final EmployeeService service;

    public EmployeeController(EmployeeService service) {
        this.service = service;
    }

    @GetMapping
    public List<Employee> getAll() {
        return service.getEmployees();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Employee> getOne(
        @PathVariable Long id
    ) {
        return service.getEmployee(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
}
""",
        "passed_tests": 9,
        "review_scores": {
            "requirement_coverage": 94,
            "code_quality": 92,
            "readability": 90
        }
    },

    {
        "candidate_id": "CAND006",
        "job_id": "JD002",
        "task_id": "PYTHON_TASK_006",
        "title": "Python Candidate Matching",
        "requirements": [
            "Compare candidate skills",
            "Match required job skills",
            "Calculate matching percentage",
            "Handle missing skills"
        ],
        "candidate_code": """
def calculate_skill_match(candidate_skills, required_skills):

    candidate_skills = {
        skill.lower() for skill in candidate_skills
    }

    required_skills = {
        skill.lower() for skill in required_skills
    }

    if not required_skills:
        return 0

    matched = candidate_skills.intersection(
        required_skills
    )

    percentage = (
        len(matched) / len(required_skills)
    ) * 100

    return round(percentage, 2)


candidate = ["Python", "Django", "SQL"]
required = ["Python", "Django", "SQL", "Git"]

print(calculate_skill_match(candidate, required))
""",
        "passed_tests": 8,
        "review_scores": {
            "requirement_coverage": 90,
            "code_quality": 88,
            "readability": 86
        }
    },

    {
        "candidate_id": "CAND007",
        "job_id": "JD001",
        "task_id": "MERN_TASK_007",
        "title": "Node.js REST API",
        "requirements": [
            "Create REST API endpoint",
            "Validate request parameters",
            "Return JSON response",
            "Handle errors"
        ],
        "candidate_code": """
const express = require('express');

const app = express();

app.use(express.json());

app.get('/api/employees/:id', (req, res) => {

    const id = Number(req.params.id);

    if (!Number.isInteger(id) || id <= 0) {
        return res.status(400).json({
            message: 'Invalid employee ID'
        });
    }

    res.json({
        id: id,
        name: 'Demo Employee'
    });
});

app.listen(3000);
""",
        "passed_tests": 8,
        "review_scores": {
            "requirement_coverage": 84,
            "code_quality": 82,
            "readability": 85
        }
    },

    {
        "candidate_id": "CAND008",
        "job_id": "JD002",
        "task_id": "PYTHON_TASK_008",
        "title": "Python Data Filtering",
        "requirements": [
            "Filter records by department",
            "Return matching employees",
            "Handle empty records",
            "Use reusable functions"
        ],
        "candidate_code": """
def filter_by_department(employees, department):

    if not employees:
        return []

    result = []

    for employee in employees:

        if employee.get("department") == department:
            result.append(employee)

    return result


employees = [
    {"name": "Anu", "department": "IT"},
    {"name": "Ravi", "department": "HR"},
    {"name": "Meera", "department": "IT"}
]

print(filter_by_department(employees, "IT"))
""",
        "passed_tests": 6,
        "review_scores": {
            "requirement_coverage": 75,
            "code_quality": 72,
            "readability": 78
        }
    },

    {
        "candidate_id": "CAND009",
        "job_id": "JD001",
        "task_id": "MERN_TASK_009",
        "title": "React Employee Search",
        "requirements": [
            "Create employee search",
            "Filter employee records",
            "Handle case-insensitive search",
            "Display matching records"
        ],
        "candidate_code": """
import React, { useState } from 'react';

function EmployeeSearch() {

    const employees = [
        "Anu",
        "Arun",
        "Meera",
        "Karthik"
    ];

    const [search, setSearch] = useState('');

    const filteredEmployees = employees.filter(
        employee =>
            employee.toLowerCase().includes(
                search.toLowerCase()
            )
    );

    return (
        <div>
            <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search employee"
            />

            <ul>
                {filteredEmployees.map(employee => (
                    <li key={employee}>{employee}</li>
                ))}
            </ul>
        </div>
    );
}

export default EmployeeSearch;
""",
        "passed_tests": 8,
        "review_scores": {
            "requirement_coverage": 88,
            "code_quality": 85,
            "readability": 88
        }
    }

]


# ============================================================
# 2. GENERATE JSON SUBMISSIONS
# ============================================================

def generate_submissions():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    generated_count = 0

    for candidate in DEMO_CANDIDATES:

        candidate_id = candidate["candidate_id"]

        candidate_number = candidate_id.replace(
            "CAND",
            ""
        )

        submission = {

            "candidate_id": candidate_id,

            "job_id": candidate["job_id"],

            "assessment_type": "MACHINE_TEST",

            "data_type": "SIMULATED_DEMO_DATA",

            "is_simulated": True,

            "score_source": "SIMULATED_DEMO_INPUT",

            "test_results_are_simulated": True,

            "review_scores_are_simulated": True,

            "generated_at": datetime.now().astimezone().isoformat(),

            "task": {

                "task_id": candidate["task_id"],

                "title": candidate["title"],

                "requirements": candidate["requirements"],

                "candidate_code": candidate["candidate_code"],

                "test_results": {

                    "total_tests": 10,

                    "passed_tests": candidate["passed_tests"],

                    "failed_tests": (
                        10 - candidate["passed_tests"]
                    ),

                    "is_simulated": True,

                    "execution_status": "SIMULATED_NOT_EXECUTED"
                },

                "review_scores": {

                    **candidate["review_scores"],

                    "is_simulated": True,

                    "review_status": "SIMULATED_NOT_HUMAN_REVIEWED"
                }
            }
        }

        file_name = (
            f"candidate_{candidate_number}_machine_test.json"
        )

        file_path = OUTPUT_DIR / file_name

        with file_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                submission,
                file,
                indent=4,
                ensure_ascii=False
            )

        generated_count += 1

        print("Generated:", file_name)

    print("\n" + "=" * 60)
    print("MACHINE TEST DEMO DATA GENERATION SUMMARY")
    print("=" * 60)

    print("Generated submissions:", generated_count)
    print("CAND010:", "NOT_PROVIDED")
    print("Data type:", "SIMULATED_DEMO_DATA")
    print("Test execution:", "NOT ACTUALLY EXECUTED")
    print("Human review:", "NOT ACTUALLY PERFORMED")

    print("\nOutput folder:")
    print(OUTPUT_DIR)


# ============================================================
# 3. MAIN
# ============================================================

if __name__ == "__main__":
    generate_submissions()
