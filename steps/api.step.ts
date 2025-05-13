// Import required dependencies
import { ApiRouteConfig, StepHandler } from 'motia';
import { z } from 'zod';

// Define input schema for lesson notes
const inputSchema = z.object({
  subject: z.string().min(1, 'Subject is required'),
  class_level: z.string().min(1, 'Class level is required'),
  topic: z.string().min(1, 'Topic is required'),
  week_ending: z.string().min(1, 'Week ending is required'),
  cls_size: z.record(z.string(), z.number().int().positive('Class size must be a dictionary of class names to positive integers')).optional().default({}),
  duration: z.string().min(1, 'Duration is required'),
  days: z.string().min(1, 'Days are required'),
  week: z.string().min(1, 'Week is required'),
  phone_number: z.string().min(1, 'User phone is required'),
  email: z.string().email('Invalid email address').optional(),
  custom_instructions: z.string().optional().default(''),
});

// Define Motia API route configuration
export const config: ApiRouteConfig = {
  type: 'api',
  name: 'Lesson Notes Generator',
  description: 'Generates lesson notes customized for Morning Star School',
  path: '/lng/v1/generate-notes',
  virtualSubscribes: ['/generate-notes'],
  method: 'POST',
  emits: ['generate-notes'],
  bodySchema: inputSchema,
  flows: ['default'],
};

// Define handler for the API route
export const handler: StepHandler<typeof config> = async (req, { logger, emit }) => {
  // Log request processing
  logger.info('Processing default flow API step', req.body);

  // Extract and structure lesson notes data
  const { subject, class_level, topic, week_ending, cls_size, duration, days, week, custom_instructions, phone_number, email } = req.body;
  const lesson_notes = {
    subject,
    class_level,
    topic,
    week_ending,
    cls_size,
    duration,
    days,
    week,
    custom_instructions
  };

  // Log emitted data for debugging
  logger.info('Emitting generate-notes with data:', { lesson_notes });

  // Emit generate-notes event
  await emit({
    topic: 'generate-notes',
    data: { lesson_notes, phone_number, email },
  });

  // Return success response
  return {
    status: 200,
    body: { message: 'Generate-notes topic emitted' },
  };
};