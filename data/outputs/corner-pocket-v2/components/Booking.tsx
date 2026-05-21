'use client';

import { useState, useRef, useId } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

type FormState = 'idle' | 'submitting' | 'success' | 'error';

interface Field {
  id: string;
  label: string;
  type: string;
  placeholder?: string;
  options?: string[];
  required?: boolean;
  min?: string;
  max?: string;
}

const FIELDS: Field[] = [
  { id: 'name', label: 'Full Name', type: 'text', placeholder: 'Rohit Verma', required: true },
  { id: 'phone', label: 'Phone Number', type: 'tel', placeholder: '+91 98765 43210', required: true },
  { id: 'date', label: 'Preferred Date', type: 'date', required: true },
  {
    id: 'time',
    label: 'Preferred Time',
    type: 'select',
    options: [
      'Morning (12pm – 3pm)',
      'Afternoon (3pm – 6pm)',
      'Evening (6pm – 9pm)',
      'Night (9pm – 12am)',
      'Late Night (12am – 2am)',
    ],
    required: true,
  },
  {
    id: 'table',
    label: 'Table Preference',
    type: 'select',
    options: [
      'Any Available',
      'Snooker — Tournament Table',
      'American Pool Table',
      'VIP Private Room',
    ],
    required: false,
  },
  { id: 'players', label: 'Number of Players', type: 'number', placeholder: '2', min: '1', max: '8', required: true },
];

// Float-label input — Material-style animation
interface FloatFieldProps {
  field: Field;
  value: string;
  onChange: (val: string) => void;
}

function FloatField({ field, value, onChange }: FloatFieldProps) {
  const [focused, setFocused] = useState(false);
  const uid = useId();
  const labelId = `${uid}-label`;
  const inputId = `${uid}-input`;

  const hasContent = value.length > 0;
  const labelUp = focused || hasContent;

  const baseInput =
    'w-full bg-transparent border-b border-brass/30 pb-2 pt-6 text-cream font-body text-sm outline-none transition-colors focus:border-gold placeholder:text-transparent';

  return (
    <div className="relative group">
      <label
        id={labelId}
        htmlFor={inputId}
        className="absolute left-0 font-mono text-xs tracking-[0.12em] uppercase cursor-text transition-all duration-300 pointer-events-none"
        style={{
          top: labelUp ? '0' : '1.5rem',
          fontSize: labelUp ? '0.55rem' : '0.75rem',
          color: focused ? '#d4af37' : 'rgba(176,141,87,0.7)',
          transform: labelUp ? 'none' : 'none',
        }}
      >
        {field.label}{field.required && <span className="text-gold/60 ml-1" aria-label="required">*</span>}
      </label>

      {field.type === 'select' ? (
        <select
          id={inputId}
          aria-labelledby={labelId}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className={`${baseInput} cursor-pointer`}
          style={{
            colorScheme: 'dark',
            background: 'transparent',
            appearance: 'none',
            WebkitAppearance: 'none',
          }}
          required={field.required}
          aria-required={field.required}
        >
          <option value="" disabled style={{ background: '#0a0d0a' }}>
            Select {field.label}
          </option>
          {field.options?.map((opt) => (
            <option key={opt} value={opt} style={{ background: '#0a0d0a', color: '#f5e6c8' }}>
              {opt}
            </option>
          ))}
        </select>
      ) : (
        <input
          id={inputId}
          aria-labelledby={labelId}
          type={field.type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={field.placeholder}
          min={field.min}
          max={field.max}
          required={field.required}
          aria-required={field.required}
          className={baseInput}
          style={{ colorScheme: 'dark' }}
        />
      )}

      {/* Animated bottom border highlight */}
      <div
        className="absolute bottom-0 left-0 h-px bg-gold transition-all duration-400"
        style={{
          width: focused ? '100%' : '0%',
          transitionTimingFunction: 'cubic-bezier(0.16, 1, 0.3, 1)',
        }}
        aria-hidden="true"
      />
    </div>
  );
}

export function Booking() {
  const formRef = useRef<HTMLFormElement>(null);
  const [formState, setFormState] = useState<FormState>('idle');
  const [values, setValues] = useState<Record<string, string>>(
    Object.fromEntries(FIELDS.map((f) => [f.id, '']))
  );

  const updateField = (id: string) => (val: string) => {
    setValues((prev) => ({ ...prev, [id]: val }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormState('submitting');

    // REPLACE: swap with Formspree endpoint — see README
    // const res = await fetch('https://formspree.io/f/YOUR_FORM_ID', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    //   body: JSON.stringify(values),
    // });

    // Simulated delay for demo
    await new Promise((r) => setTimeout(r, 1200));
    setFormState('success');
  };

  return (
    <section
      id="booking"
      className="relative py-32 md:py-48"
      aria-label="Book a Table"
    >
      {/* Felt-dark background with subtle grid */}
      <div
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(180deg, #0a0d0a 0%, #0c1a10 50%, #0a0d0a 100%)',
          backgroundImage:
            'linear-gradient(rgba(26,107,70,0.05) 1px, transparent 1px), linear-gradient(to right, rgba(26,107,70,0.05) 1px, transparent 1px)',
          backgroundSize: '60px 60px',
        }}
        aria-hidden="true"
      />

      <div className="relative z-10 max-w-screen-xl mx-auto px-6 md:px-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24 items-start">
          {/* Left: copy */}
          <div>
            <div className="flex items-center gap-4 mb-8">
              <span className="gold-rule max-w-[60px]" aria-hidden="true" />
              <span className="font-mono text-xs tracking-[0.35em] text-brass/70 uppercase">
                Reservations
              </span>
            </div>
            <h2
              className="font-display font-light text-cream leading-tight mb-6"
              style={{ fontSize: 'clamp(2.5rem, 5vw, 4rem)' }}
            >
              Reserve<br />
              <em className="text-gold-gradient not-italic" style={{ fontStyle: 'italic' }}>
                Your Table.
              </em>
            </h2>
            <p className="font-body text-cream/60 leading-relaxed max-w-sm mb-8">
              Walk-ins welcome. But the best tables go to those who book. Minimum 1 hour,
              max 4 hours per session. Late-night sessions until 2am on weekends.
            </p>

            {/* Operational details */}
            <dl className="flex flex-col gap-4">
              {[
                { dt: 'Hours', dd: 'Mon–Thu 12pm – 2am · Fri–Sun 11am – 3am' },
                { dt: 'Walk-in Rate', dd: '₹350/hr per table (off-peak) · ₹500/hr (peak)' },
                { dt: 'Members', dd: 'Members get 10–20% off + priority booking' },
                { dt: 'Call us', dd: '+91-22-4567-8900' },
              ].map(({ dt, dd }) => (
                <div key={dt} className="flex gap-4">
                  <dt className="font-mono text-xs tracking-[0.15em] text-brass uppercase flex-shrink-0 w-28">
                    {dt}
                  </dt>
                  <dd className="font-body text-cream/60 text-sm">{dd}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* Right: form */}
          <div
            className="relative p-8 rounded-sm"
            style={{
              background: 'rgba(10,13,10,0.8)',
              border: '1px solid rgba(176,141,87,0.18)',
              boxShadow: '0 32px 64px rgba(0,0,0,0.5)',
              backdropFilter: 'blur(8px)',
            }}
          >
            {/* Top brass accent */}
            <div
              className="absolute top-0 left-8 right-8 h-px"
              style={{
                background: 'linear-gradient(90deg, transparent 0%, rgba(212,175,55,0.5) 50%, transparent 100%)',
              }}
              aria-hidden="true"
            />

            <AnimatePresence mode="wait">
              {formState === 'success' ? (
                <motion.div
                  key="success"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex flex-col items-center justify-center py-16 text-center gap-6"
                  role="alert"
                  aria-live="polite"
                >
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center"
                    style={{ border: '1px solid rgba(212,175,55,0.4)', background: 'rgba(212,175,55,0.08)' }}
                    aria-hidden="true"
                  >
                    <span className="text-gold text-2xl">◆</span>
                  </div>
                  <h3 className="font-display text-2xl text-cream">Table Reserved</h3>
                  <p className="font-body text-cream/60 text-sm max-w-xs">
                    We'll call you within 30 minutes to confirm your booking. See you at the table.
                  </p>
                  <button
                    onClick={() => {
                      setFormState('idle');
                      setValues(Object.fromEntries(FIELDS.map((f) => [f.id, ''])));
                    }}
                    className="font-mono text-xs tracking-[0.2em] text-brass hover:text-gold uppercase transition-colors"
                  >
                    Make another booking
                  </button>
                </motion.div>
              ) : (
                <motion.form
                  key="form"
                  ref={formRef}
                  onSubmit={handleSubmit}
                  noValidate
                  aria-label="Table booking form"
                >
                  <h3 className="font-display font-light text-cream mb-8" style={{ fontSize: '1.5rem' }}>
                    Book a Table
                  </h3>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 mb-10">
                    {FIELDS.map((field) => (
                      <div
                        key={field.id}
                        className={field.id === 'name' || field.id === 'phone' ? 'sm:col-span-1' : 'sm:col-span-1'}
                      >
                        <FloatField
                          field={field}
                          value={values[field.id] ?? ''}
                          onChange={updateField(field.id)}
                        />
                      </div>
                    ))}
                  </div>

                  {/* Submit — magnetic hover via CSS */}
                  <button
                    type="submit"
                    disabled={formState === 'submitting'}
                    className="magnetic-btn w-full py-4 font-mono text-sm tracking-[0.15em] uppercase rounded-sm transition-all duration-300 relative overflow-hidden group"
                    style={{
                      background: 'linear-gradient(90deg, #b08d57, #d4af37)',
                      color: '#0a0d0a',
                    }}
                    aria-label={formState === 'submitting' ? 'Submitting booking…' : 'Submit booking request'}
                  >
                    {/* Ripple overlay on click */}
                    <span
                      className="absolute inset-0 scale-0 rounded-sm group-active:scale-100 transition-transform duration-500 origin-center"
                      style={{ background: 'rgba(255,255,255,0.15)' }}
                      aria-hidden="true"
                    />
                    <span className="relative">
                      {formState === 'submitting' ? 'Sending…' : 'Confirm Booking'}
                    </span>
                  </button>

                  <p className="font-mono text-[0.6rem] text-cream/25 text-center mt-4 tracking-wider">
                    We'll confirm by phone within 30 minutes. No credit card required.
                  </p>
                </motion.form>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
}
