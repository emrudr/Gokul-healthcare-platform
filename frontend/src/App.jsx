import React, { useState, useEffect, useRef } from 'react';
import { api } from './api';

// ─── HELPERS ──────────────────────────────────────────────────────────────────

function buildDate() {
  const d = new Date();
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${dd}.${mm}.${yyyy}`;
}

const VERSION_DATE = '26.10.2026';

// ─── SPINNER ──────────────────────────────────────────────────────────────────
function Spinner({ dark }) {
  return <span className={`spinner${dark ? ' spinner--dark' : ''}`} />;
}

// ─── ALERT BANNER ─────────────────────────────────────────────────────────────
function Alert({ type = 'error', message, onDismiss }) {
  const icons = { error: '!', success: 'OK', warning: '!' };
  if (!message) return null;
  return (
    <div className={`alert alert--${type}`}>
      <span className="alert__icon">{icons[type]}</span>
      <span className="alert__msg">{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          style={{ background: 'none', border: 'none', cursor: 'pointer', marginLeft: 'auto', fontSize: '14px', opacity: 0.6 }}
        >
          X
        </button>
      )}
    </div>
  );
}

// ─── PATIENT MODAL ─────────────────────────────────────────────────────────────
function PatientModal({ patient, mode, onClose, onSaved, onDeleted }) {
  const isEdit = mode === 'edit';

  const [form, setForm] = useState({
    full_name: patient?.full_name ?? '',
    dob: patient?.dob ?? '',
    email: patient?.email ?? '',
    glucose: patient?.glucose ?? '',
    haemoglobin: patient?.haemoglobin ?? '',
    cholesterol: patient?.cholesterol ?? '',
  });
  const [remarks, setRemarks] = useState(patient?.remarks ?? '');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [checkingRemarks, setCheckingRemarks] = useState(false);

  const firstInputRef = useRef(null);
  useEffect(() => {
    setTimeout(() => firstInputRef.current?.focus(), 80);
  }, []);

  function handleChange(e) {
    setError('');
    setSuccess('');
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleCheckRemarks() {
    setError('');
    const g = parseFloat(form.glucose);
    const h = parseFloat(form.haemoglobin);
    const c = parseFloat(form.cholesterol);
    if (!g || !h || !c) {
      setError('Please enter valid numeric values for Glucose, Haemoglobin, and Cholesterol before checking remarks.');
      return;
    }
    setCheckingRemarks(true);
    try {
      let result;
      if (isEdit && patient?.id) {
        result = await api.checkRemarks(patient.id);
        setRemarks(result.remarks ?? '');
      } else {
        result = await api.previewRemarks({ glucose: g, haemoglobin: h, cholesterol: c });
        setRemarks(result.remarks ?? '');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setCheckingRemarks(false);
    }
  }

  async function handleSave() {
    setError('');
    setSuccess('');
    setSaving(true);
    try {
      const payload = {
        full_name: form.full_name,
        dob: form.dob,
        email: form.email,
        glucose: parseFloat(form.glucose),
        haemoglobin: parseFloat(form.haemoglobin),
        cholesterol: parseFloat(form.cholesterol),
        remarks,
      };
      let saved;
      if (isEdit) {
        saved = await api.updatePatient(patient.id, payload);
      } else {
        saved = await api.createPatient(payload);
      }
      setSuccess(isEdit ? 'Patient record updated successfully.' : 'New patient record created successfully.');
      setTimeout(() => {
        onSaved(saved);
        onClose();
      }, 800);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    const confirmed = window.confirm(
      `Are you sure you want to delete the record for "${patient?.full_name}"?\n\nThis action cannot be undone.`
    );
    if (!confirmed) return;
    setDeleting(true);
    setError('');
    try {
      await api.deletePatient(patient.id);
      onDeleted(patient.id);
      onClose();
    } catch (err) {
      setError(err.message);
      setDeleting(false);
    }
  }

  function handleOverlayClick(e) {
    if (e.target === e.currentTarget) onClose();
  }

  return (
    <div className="modal-overlay" onClick={handleOverlayClick} role="dialog" aria-modal="true">
      <div className="modal">
        {/* HEADER */}
        <div className="modal__header">
          <div>
            <div className="modal__title">
              {isEdit ? 'Patient Details' : 'Add New Patient'}
            </div>
            {isEdit && patient?.id && (
              <div className="modal__subtitle">Patient ID #{patient.id} | {patient.full_name}</div>
            )}
          </div>
          <button className="modal__close" onClick={onClose} aria-label="Close modal">X</button>
        </div>

        {/* BODY */}
        <div className="modal__body">
          {error && <Alert type="error" message={error} onDismiss={() => setError('')} />}
          {success && <Alert type="success" message={success} />}

          <div className="section-divider">Patient Information</div>
          <div className="form-grid">
            <div className="form-field form-field--full">
              <label className="form-label" htmlFor="m-full_name">Full Name</label>
              <input
                ref={firstInputRef}
                id="m-full_name"
                className="form-input"
                name="full_name"
                value={form.full_name}
                onChange={handleChange}
                placeholder="e.g. Eleanor Vance"
                autoComplete="off"
              />
            </div>
            <div className="form-field">
              <label className="form-label" htmlFor="m-dob">Date of Birth (DD.MM.YYYY)</label>
              <input
                id="m-dob"
                className="form-input"
                name="dob"
                value={form.dob}
                onChange={handleChange}
                placeholder="15.08.1990"
                autoComplete="off"
              />
            </div>
            <div className="form-field">
              <label className="form-label" htmlFor="m-email">Email Address</label>
              <input
                id="m-email"
                className="form-input"
                name="email"
                value={form.email}
                onChange={handleChange}
                placeholder="patient@example.com"
                autoComplete="off"
              />
            </div>
          </div>

          <div className="section-divider" style={{ marginTop: 8 }}>Biomarker Values</div>
          <div className="form-grid">
            <div className="form-field">
              <label className="form-label" htmlFor="m-glucose">Glucose (mg/dL)</label>
              <input
                id="m-glucose"
                className="form-input"
                name="glucose"
                type="number"
                step="any"
                value={form.glucose}
                onChange={handleChange}
                placeholder="e.g. 95"
              />
            </div>
            <div className="form-field">
              <label className="form-label" htmlFor="m-haemoglobin">Haemoglobin (g/dL)</label>
              <input
                id="m-haemoglobin"
                className="form-input"
                name="haemoglobin"
                type="number"
                step="any"
                value={form.haemoglobin}
                onChange={handleChange}
                placeholder="e.g. 14.2"
              />
            </div>
            <div className="form-field form-field--full">
              <label className="form-label" htmlFor="m-cholesterol">Total Cholesterol (mg/dL)</label>
              <input
                id="m-cholesterol"
                className="form-input"
                name="cholesterol"
                type="number"
                step="any"
                value={form.cholesterol}
                onChange={handleChange}
                placeholder="e.g. 185"
              />
            </div>
          </div>

          {/* REMARKS */}
          <div className="section-divider" style={{ marginTop: 8 }}>Clinical Remarks</div>
          <div className="remarks-section" style={{ marginBottom: 0 }}>
            <div className="remarks-header">
              <span className="remarks-label">AI Health Assessment</span>
              <button
                className="btn btn--ghost"
                onClick={handleCheckRemarks}
                disabled={checkingRemarks}
              >
                {checkingRemarks ? <><Spinner dark /> Checking...</> : 'Check Remarks'}
              </button>
            </div>
            <div className="remarks-body">
              {remarks ? (
                <p className="remarks-text">{remarks}</p>
              ) : (
                <p className="remarks-empty">
                  No remarks yet. Click "Check Remarks" to generate an AI clinical assessment.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* FOOTER */}
        <div className="modal__footer">
          <div>
            {isEdit && (
              <button
                className="btn btn--danger"
                onClick={handleDelete}
                disabled={deleting || saving}
              >
                {deleting ? <><Spinner /> Deleting...</> : 'Delete Patient'}
              </button>
            )}
          </div>
          <div className="modal__footer-right">
            <button className="btn btn--secondary" onClick={onClose} disabled={saving || deleting}>
              Cancel
            </button>
            <button
              className="btn btn--primary"
              onClick={handleSave}
              disabled={saving || deleting}
            >
              {saving
                ? <><Spinner /> {isEdit ? 'Updating...' : 'Saving...'}</>
                : isEdit ? 'Upload Changes' : 'Save Patient'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── MAIN APP ─────────────────────────────────────────────────────────────────
export default function App() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState('');
  const [modal, setModal] = useState(null); // null | { mode: 'create' | 'edit', patient: {...} | null }
  const [tableSuccess, setTableSuccess] = useState('');

  async function loadPatients() {
    setLoading(true);
    setFetchError('');
    try {
      const data = await api.getPatients();
      setPatients(data);
    } catch (err) {
      setFetchError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadPatients(); }, []);

  function openCreate() {
    setModal({ mode: 'create', patient: null });
  }

  function openEdit(patient) {
    setModal({ mode: 'edit', patient });
  }

  function closeModal() {
    setModal(null);
  }

  function handleSaved(saved) {
    setTableSuccess(
      modal?.mode === 'edit'
        ? `Patient #${saved.id} (${saved.full_name}) updated successfully.`
        : `New patient ${saved.full_name} (ID #${saved.id}) created successfully.`
    );
    loadPatients();
    setTimeout(() => setTableSuccess(''), 5000);
  }

  function handleDeleted(id) {
    setPatients((prev) => prev.filter((p) => p.id !== id));
    setTableSuccess(`Patient #${id} deleted successfully.`);
    setTimeout(() => setTableSuccess(''), 5000);
  }

  return (
    <>
      {/* TOP NAV STRIP */}
      <nav className="top-nav">
        <div className="top-nav__logo">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <rect x="1" y="1" width="8" height="8" fill="#4589ff"/>
            <rect x="11" y="1" width="8" height="8" fill="#4589ff" opacity="0.7"/>
            <rect x="1" y="11" width="8" height="8" fill="#4589ff" opacity="0.5"/>
            <rect x="11" y="11" width="8" height="8" fill="#4589ff" opacity="0.3"/>
          </svg>
          Gokul Healthcare Platform
        </div>
      </nav>

      {/* PAGE HEADER */}
      <header className="page-header">
        <h1 className="page-header__title">Gokul Healthcare Platform</h1>
        <p className="page-header__subtitle">Task2 - prepared by Rudransh</p>
      </header>

      {/* MAIN CONTENT */}
      <main className="main-content">

        {/* CONNECTION ERROR */}
        {fetchError && (
          <div style={{ marginTop: 16 }}>
            <Alert type="error" message={`Backend connection error: ${fetchError}. Make sure the FastAPI server is running on port 8000.`} />
          </div>
        )}

        {/* SUCCESS BANNER */}
        {tableSuccess && (
          <div style={{ marginTop: 16 }}>
            <Alert type="success" message={tableSuccess} onDismiss={() => setTableSuccess('')} />
          </div>
        )}

        {/* ACTION BAR */}
        <div className="action-bar" style={{ marginTop: 16 }}>
          <div className="action-bar__left">
            <button className="btn btn--primary" onClick={openCreate}>
              + Add New Patient
            </button>
            <span className="action-bar__count">
              {!loading && `${patients.length} record${patients.length !== 1 ? 's' : ''}`}
            </span>
          </div>
          <button
            className="btn btn--secondary"
            onClick={loadPatients}
            disabled={loading}
            title="Refresh patient list"
          >
            {loading ? <Spinner dark /> : null} Refresh
          </button>
        </div>

        {/* DATA TABLE */}
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Full Name</th>
                <th>Date of Birth</th>
                <th>Email Address</th>
                <th style={{ textAlign: 'right' }}>Glucose</th>
                <th style={{ textAlign: 'right' }}>Haemoglobin</th>
                <th style={{ textAlign: 'right' }}>Cholesterol</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr className="loading-row">
                  <td colSpan={8}>
                    <Spinner dark /> Loading patient records...
                  </td>
                </tr>
              ) : patients.length === 0 ? (
                <tr>
                  <td colSpan={8}>
                    <div className="empty-state">
                      <div className="empty-state__icon">
                        <svg width="40" height="40" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <rect x="2" y="8" width="28" height="20" rx="0" stroke="#A8A8A8" strokeWidth="1.5" fill="none"/>
                          <rect x="2" y="8" width="28" height="6" fill="#E0E0E0"/>
                          <line x1="12" y1="11" x2="20" y2="11" stroke="#A8A8A8" strokeWidth="1.5"/>
                          <rect x="2" y="2" width="28" height="6" fill="#C6C6C6" stroke="#A8A8A8" strokeWidth="1.5"/>
                        </svg>
                      </div>
                      <div className="empty-state__msg">No patient records found</div>
                      <div className="empty-state__sub">Click "Add New Patient" to create the first record</div>
                    </div>
                  </td>
                </tr>
              ) : (
                patients.map((p) => (
                  <tr key={p.id} onClick={() => openEdit(p)} title="Click to view / edit patient">
                    <td className="td--id">{p.id}</td>
                    <td className="td--name">{p.full_name}</td>
                    <td>{p.dob}</td>
                    <td>{p.email}</td>
                    <td className="td--num">{p.glucose}</td>
                    <td className="td--num">{p.haemoglobin}</td>
                    <td className="td--num">{p.cholesterol}</td>
                    <td
                      className="td--remarks"
                      title={p.remarks || undefined}
                    >
                      {p.remarks || (
                        <span style={{ color: 'var(--gray-40)', fontStyle: 'italic' }}>-</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>

      {/* FOOTER */}
      <footer className="footer">
        <strong>Prepared by Rudransh Mishra</strong>
        <span className="sep">|</span>
        Phone: +91 7607802666
        <span className="sep">|</span>
        Email: emrudr@gmail.com
        <span className="sep">|</span>
        Version Date: {VERSION_DATE}
      </footer>

      {/* MODAL */}
      {modal && (
        <PatientModal
          mode={modal.mode}
          patient={modal.patient}
          onClose={closeModal}
          onSaved={handleSaved}
          onDeleted={handleDeleted}
        />
      )}
    </>
  );
}
