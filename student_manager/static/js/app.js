/**
 * Client-side Controller for Student Management System
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const searchInput = document.getElementById('searchInput');
    const departmentFilter = document.getElementById('departmentFilter');
    const statusFilter = document.getElementById('statusFilter');
    const studentsTableBody = document.getElementById('studentsTableBody');
    const emptyState = document.getElementById('emptyState');
    
    // Stats Elements
    const statTotalStudents = document.getElementById('statTotalStudents');
    const statDeptCount = document.getElementById('statDeptCount');
    const statAvgGpa = document.getElementById('statAvgGpa');
    const statDeansList = document.getElementById('statDeansList');
    const statProbation = document.getElementById('statProbation');
    
    // Modal & Buttons
    const openAddModalBtn = document.getElementById('openAddModalBtn');
    const seedDataBtn = document.getElementById('seedDataBtn');
    const studentModal = document.getElementById('studentModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelModalBtn = document.getElementById('cancelModalBtn');
    const studentForm = document.getElementById('studentForm');

    // Load initial data
    loadStudents();
    loadStats();

    // Event Listeners
    searchInput.addEventListener('input', debounce(() => loadStudents(), 300));
    departmentFilter.addEventListener('change', () => loadStudents());
    statusFilter.addEventListener('change', () => loadStudents());

    openAddModalBtn.addEventListener('click', () => {
        studentForm.reset();
        studentModal.classList.remove('hidden');
    });

    closeModalBtn.addEventListener('click', () => studentModal.classList.add('hidden'));
    cancelModalBtn.addEventListener('click', () => studentModal.classList.add('hidden'));

    studentModal.addEventListener('click', (e) => {
        if (e.target === studentModal) {
            studentModal.classList.add('hidden');
        }
    });

    studentForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleSaveStudent();
    });

    seedDataBtn.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/seed', { method: 'POST' });
            if (res.ok) {
                showToast('Sample records reseeded successfully!', 'success');
                loadStudents();
                loadStats();
            } else {
                showToast('Failed to seed records', 'error');
            }
        } catch (err) {
            showToast('Network error while seeding', 'error');
        }
    });

    // Fetch and display students
    async function loadStudents() {
        const query = searchInput.value.trim();
        const dept = departmentFilter.value;
        const status = statusFilter.value;

        const params = new URLSearchParams();
        if (query) params.append('search', query);
        if (dept) params.append('dept', dept);
        if (status) params.append('status', status);

        try {
            const res = await fetch(`/api/students?${params.toString()}`);
            if (!res.ok) throw new Error('Failed to fetch students');
            const students = await res.json();
            renderStudentsTable(students);
        } catch (err) {
            console.error(err);
            showToast('Unable to load student records', 'error');
        }
    }

    // Fetch and display dashboard statistics
    async function loadStats() {
        try {
            const res = await fetch('/api/stats');
            if (!res.ok) throw new Error('Failed to load stats');
            const stats = await res.json();
            
            statTotalStudents.textContent = stats.total_students || 0;
            statDeptCount.textContent = `Across ${stats.department_count || 0} departments`;
            statAvgGpa.textContent = stats.average_gpa !== undefined ? stats.average_gpa.toFixed(2) : '0.00';
            statDeansList.textContent = stats.deans_list_count || 0;
            statProbation.textContent = stats.probation_count || 0;
        } catch (err) {
            console.error('Stats error:', err);
        }
    }

    // Render table rows
    function renderStudentsTable(students) {
        studentsTableBody.innerHTML = '';

        if (!students || students.length === 0) {
            emptyState.classList.remove('hidden');
            return;
        }

        emptyState.classList.add('hidden');

        students.forEach(s => {
            const tr = document.createElement('tr');
            
            // Status class
            let statusBadgeClass = 'status-good';
            if (s.status === "Dean's List") statusBadgeClass = 'status-deans';
            else if (s.status === "Academic Probation") statusBadgeClass = 'status-probation';

            // Course badges
            const coursesHtml = (s.courses || []).length > 0 
                ? s.courses.map(c => `<span class="course-tag">${escapeHtml(c)}</span>`).join('')
                : '<span class="text-muted" style="font-size:0.8rem">No courses</span>';

            tr.innerHTML = `
                <td><span class="student-code">${escapeHtml(s.student_id)}</span></td>
                <td>
                    <div class="student-name">${escapeHtml(s.name)}</div>
                    <div class="student-email">${escapeHtml(s.email)}</div>
                </td>
                <td>${escapeHtml(s.department)}</td>
                <td><div class="course-tags">${coursesHtml}</div></td>
                <td>${s.attendance.toFixed(1)}%</td>
                <td><span class="gpa-score">${s.gpa.toFixed(2)}</span></td>
                <td><span class="status-badge ${statusBadgeClass}">${escapeHtml(s.status)}</span></td>
                <td class="text-right">
                    <div class="action-btns">
                        <button class="btn-icon btn-icon-delete" data-id="${s.student_id}" title="Delete Student">
                            <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                        </button>
                    </div>
                </td>
            `;

            const delBtn = tr.querySelector('.btn-icon-delete');
            delBtn.addEventListener('click', () => handleDeleteStudent(s.student_id, s.name));

            studentsTableBody.appendChild(tr);
        });
    }

    // Save student handler
    async function handleSaveStudent() {
        const studentId = document.getElementById('formStudentId').value.trim();
        const name = document.getElementById('formName').value.trim();
        const email = document.getElementById('formEmail').value.trim();
        const department = document.getElementById('formDepartment').value.trim();
        const attendance = parseFloat(document.getElementById('formAttendance').value) || 100.0;
        
        // Parse courses
        const coursesRaw = document.getElementById('formCourses').value.trim();
        const courses = coursesRaw ? coursesRaw.split(',').map(c => c.trim()).filter(c => c) : [];

        // Parse grades (e.g. Cloud: 90, ML: 85)
        const gradesRaw = document.getElementById('formGrades').value.trim();
        const grades = {};
        if (gradesRaw) {
            const gradePairs = gradesRaw.split(',');
            for (const pair of gradePairs) {
                const parts = pair.split(':');
                if (parts.length === 2) {
                    const cName = parts[0].trim();
                    const gVal = parseFloat(parts[1].trim());
                    if (cName && !isNaN(gVal)) {
                        grades[cName] = gVal;
                        if (!courses.includes(cName)) {
                            courses.push(cName);
                        }
                    }
                }
            }
        }

        const payload = {
            student_id: studentId,
            name,
            email,
            department,
            attendance,
            courses,
            grades
        };

        try {
            const res = await fetch('/api/students', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (res.ok) {
                showToast(`Student '${name}' added successfully!`, 'success');
                studentModal.classList.add('hidden');
                loadStudents();
                loadStats();
            } else {
                showToast(data.error || 'Failed to save student', 'error');
            }
        } catch (err) {
            console.error(err);
            showToast('Network error while saving student', 'error');
        }
    }

    // Delete student handler
    async function handleDeleteStudent(id, name) {
        if (!confirm(`Are you sure you want to delete student "${name}" (${id})?`)) {
            return;
        }

        try {
            const res = await fetch(`/api/students/${encodeURIComponent(id)}`, {
                method: 'DELETE'
            });

            if (res.ok) {
                showToast(`Student "${name}" deleted.`, 'success');
                loadStudents();
                loadStats();
            } else {
                const data = await res.json();
                showToast(data.error || 'Failed to delete student', 'error');
            }
        } catch (err) {
            console.error(err);
            showToast('Network error while deleting student', 'error');
        }
    }

    // Helpers
    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span>${escapeHtml(message)}</span>
        `;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
