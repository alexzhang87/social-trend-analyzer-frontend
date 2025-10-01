import { motion, useAnimation } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { useEffect } from 'react';
import { Package, Leaf, Briefcase, ArrowRight } from 'lucide-react';

const analyses = [
  {
    icon: Package,
    title: 'Validate a Product Idea',
    description: 'Analyze conversations around "AI-powered personal assistants" to identify top feature requests and unaddressed pain points before you write a single line of code.',
    tags: ['Product Validation', 'Feature Prioritization'],
    link: '#',
  },
  {
    icon: Leaf,
    title: 'Discover a Niche Market',
    description: 'Explore the growing demand for "sustainable packaging" to find underserved customer segments and innovative material trends for your next e-commerce venture.',
    tags: ['Market Discovery', 'Niche Strategy'],
    link: '#',
  },
  {
    icon: Briefcase,
    title: 'Create Relevant Content',
    description: 'Understand the real challenges in "the future of remote work" to create content and software solutions that truly resonate with your target audience.',
    tags: ['Content Strategy', 'Audience Research'],
    link: '#',
  },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 50 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: 'easeOut',
    },
  },
};

export function FeaturedAnalysis() {
  const controls = useAnimation();
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  useEffect(() => {
    if (inView) {
      controls.start('visible');
    }
  }, [controls, inView]);

  return (
    <div className="bg-slate-50 py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Explore the Garden of Ideas
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            See how others have used IdeaEden to discover and cultivate their ventures. Each use case is a testament to the power of a well-nurtured idea.
          </p>
        </div>
        <motion.div
          ref={ref}
          variants={containerVariants}
          initial="hidden"
          animate={controls}
          className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-8 text-left sm:mt-20 lg:mx-0 lg:max-w-none lg:grid-cols-3"
        >
          {analyses.map((analysis) => (
            <motion.a
              key={analysis.title}
              href={analysis.link}
              variants={cardVariants}
              className="group relative flex flex-col rounded-2xl border border-gray-200 bg-white p-8 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300"
            >
              <div className="flex items-center gap-x-4 mb-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                  <analysis.icon className="h-6 w-6" aria-hidden="true" />
                </div>
                <h3 className="text-lg font-semibold leading-7 text-gray-900">{analysis.title}</h3>
              </div>
              <p className="flex-grow text-base leading-7 text-gray-600">{analysis.description}</p>
              <div className="mt-6">
                {analysis.tags.map(tag => (
                  <span key={tag} className="inline-block bg-gray-100 text-gray-600 text-xs font-medium mr-2 px-2.5 py-0.5 rounded-full">
                    {tag}
                  </span>
                ))}
              </div>
              <div className="mt-6 pt-6 border-t border-gray-200/80">
                <div className="flex items-center text-teal-600 font-semibold">
                  See example analysis
                  <ArrowRight className="ml-2 h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" />
                </div>
              </div>
            </motion.a>
          ))}
        </motion.div>
      </div>
    </div>
  );
}