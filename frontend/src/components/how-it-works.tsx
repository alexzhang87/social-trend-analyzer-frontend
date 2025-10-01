import { motion, useAnimation } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { useEffect } from 'react';
import { Search, BrainCircuit, Rocket } from 'lucide-react';

const steps = [
  {
    icon: Search,
    title: '1. Ask Your Question',
    description: 'Enter any trend, product, or industry. Our AI understands your query and prepares for a deep dive into social conversations.',
  },
  {
    icon: BrainCircuit,
    title: '2. AI Analyzes the Market',
    description: 'We process millions of data points from X and Reddit, identifying trends, consumer sentiment, and crucial pain points in real-time.',
  },
  {
    icon: Rocket,
    title: '3. Get Your Action Plan',
    description: 'Receive a clear, data-driven report with market opportunities, competitive insights, and a 7-day MVP launch strategy.',
  },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.3,
    },
  },
};

const stepVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.7,
      ease: 'easeOut',
    },
  },
};

export function HowItWorks() {
  const controls = useAnimation();
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.2,
  });

  useEffect(() => {
    if (inView) {
      controls.start('visible');
    }
  }, [controls, inView]);

  return (
    <div className="bg-gradient-to-br from-background to-card py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <p className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
            How Your Idea Grows
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-200">
            Our process is designed to nurture your concepts, transforming a simple spark into a data-validated business plan.
          </p>
        </div>

        <motion.div
          ref={ref}
          variants={containerVariants}
          initial="hidden"
          animate={controls}
          className="relative mx-auto mt-20 max-w-2xl"
        >
          <div className="absolute left-6 top-6 h-full w-px bg-gradient-to-b from-primary via-secondary to-accent" aria-hidden="true" />
          
          <div className="relative">
            {steps.map((step, index) => (
              <motion.div
                key={step.title}
                variants={stepVariants}
                className={`relative flex items-start group ${index < steps.length - 1 ? 'mb-16' : ''}`}
              >
                <div className="bg-card flex-shrink-0 w-12 h-12 flex items-center justify-center rounded-full border-2 border-primary z-10">
                  <step.icon className="w-6 h-6 text-primary" />
                </div>
                <div className="ml-6">
                  <h3 className="text-lg font-semibold text-white">{step.title}</h3>
                  <p className="mt-2 text-base text-gray-200">{step.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
