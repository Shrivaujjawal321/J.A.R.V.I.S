'use client';

import { useEffect, useRef, useState } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';

// Spring configs: dot is tight/snappy, ring lags behind (feels organic)
const DOT_SPRING = { stiffness: 800, damping: 28, mass: 0.5 };
const RING_SPRING = { stiffness: 120, damping: 18, mass: 1 };

export function CustomCursor() {
  const [isPointer, setIsPointer] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [isTouchDevice, setIsTouchDevice] = useState(true);

  const rawX = useMotionValue(0);
  const rawY = useMotionValue(0);

  const dotX = useSpring(rawX, DOT_SPRING);
  const dotY = useSpring(rawY, DOT_SPRING);
  const ringX = useSpring(rawX, RING_SPRING);
  const ringY = useSpring(rawY, RING_SPRING);

  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    const isTouch = window.matchMedia('(pointer: coarse)').matches;
    setIsTouchDevice(isTouch);
    if (isTouch) return;

    document.body.classList.add('custom-cursor-active');

    const onMove = (e: MouseEvent) => {
      rawX.set(e.clientX);
      rawY.set(e.clientY);
      if (!isVisible) setIsVisible(true);
    };

    const onEnterInteractive = () => setIsPointer(true);
    const onLeaveInteractive = () => setIsPointer(false);

    const onEnterWindow = () => setIsVisible(true);
    const onLeaveWindow = () => setIsVisible(false);

    window.addEventListener('mousemove', onMove);
    document.addEventListener('mouseleave', onLeaveWindow);
    document.addEventListener('mouseenter', onEnterWindow);

    // Attach to all interactive elements
    const interactiveSelector = 'a, button, [role="button"], input, textarea, select, label, [tabindex]';
    const updateInteractiveListeners = () => {
      document.querySelectorAll(interactiveSelector).forEach((el) => {
        el.addEventListener('mouseenter', onEnterInteractive);
        el.addEventListener('mouseleave', onLeaveInteractive);
      });
    };
    updateInteractiveListeners();

    // Re-attach when DOM changes (for dynamically added elements)
    const observer = new MutationObserver(updateInteractiveListeners);
    observer.observe(document.body, { childList: true, subtree: true });

    return () => {
      window.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseleave', onLeaveWindow);
      document.removeEventListener('mouseenter', onEnterWindow);
      document.body.classList.remove('custom-cursor-active');
      observer.disconnect();
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [rawX, rawY, isVisible]);

  if (isTouchDevice) return null;

  return (
    <>
      {/* Dot — snappy, follows immediately */}
      <motion.div
        aria-hidden="true"
        className="fixed top-0 left-0 pointer-events-none z-[99999]"
        style={{
          x: dotX,
          y: dotY,
          translateX: '-50%',
          translateY: '-50%',
        }}
        animate={{ opacity: isVisible ? 1 : 0 }}
        transition={{ duration: 0.15 }}
      >
        <motion.div
          animate={{
            width: isPointer ? 6 : 8,
            height: isPointer ? 6 : 8,
            backgroundColor: isPointer ? '#d4af37' : '#f5e6c8',
          }}
          transition={{ duration: 0.2 }}
          style={{ borderRadius: '50%' }}
        />
      </motion.div>

      {/* Ring — lags behind, creates the spring trail effect */}
      <motion.div
        aria-hidden="true"
        className="fixed top-0 left-0 pointer-events-none z-[99998]"
        style={{
          x: ringX,
          y: ringY,
          translateX: '-50%',
          translateY: '-50%',
        }}
        animate={{ opacity: isVisible ? 1 : 0 }}
        transition={{ duration: 0.15 }}
      >
        <motion.div
          animate={{
            width: isPointer ? 52 : 36,
            height: isPointer ? 52 : 36,
            borderColor: isPointer ? '#d4af37' : 'rgba(176, 141, 87, 0.6)',
            borderWidth: isPointer ? 2 : 1,
          }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          style={{
            borderRadius: '50%',
            borderStyle: 'solid',
          }}
        />
      </motion.div>
    </>
  );
}
