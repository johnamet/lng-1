"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ChevronRight, ChevronLeft, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import axios from "axios"
import StepOne from "@/components/steps/step-one"
import StepTwo from "@/components/steps/step-two"
import StepThree from "@/components/steps/step-three"
import StepFour from "@/components/steps/step-four"
import StepFive from "@/components/steps/step-five"
import NotificationCard from "@/components/notification-card"

export default function Home() {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({
    subject: "",
    class_level: "",
    topic: "",
    week_ending: "",
    classes: [{ name: "Class A", size: "" }],
    duration: "",
    days: "",
    week: "",
    phone_number: "+233",
    email: "",
    custom_instructions: "",
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [notification, setNotification] = useState(null)
  const [visibleFieldIndex, setVisibleFieldIndex] = useState(0)

  const totalSteps = 5
  const progress = (currentStep / totalSteps) * 100

  // Control sequential field animations
  useEffect(() => {
    setVisibleFieldIndex(0)
    const timer = setInterval(() => {
      setVisibleFieldIndex((prev) => {
        const maxFields =
          {
            1: 3, // subject, class_level, topic
            2: 4, // week_ending, duration, days, week
            3: 1, // classes
            4: 2, // phone_number, email
            5: 1, // custom_instructions
          }[currentStep] || 0
        return prev < maxFields ? prev + 1 : prev
      })
    }, 300) // Reduced to 300ms for smoother animations
    return () => clearInterval(timer)
  }, [currentStep])

  const updateFormData = (data) => {
    setFormData((prev) => ({ ...prev, ...data }))
  }

  const validateCurrentStep = () => {
    const newErrors = {}
    switch (currentStep) {
      case 1:
        if (!formData.subject) newErrors.subject = "Subject is required"
        if (!formData.class_level) newErrors.class_level = "Class level is required"
        if (!formData.topic) newErrors.topic = "Topic is required"
        break
      case 2:
        if (!formData.week_ending) newErrors.week_ending = "Week ending is required"
        if (!formData.duration) newErrors.duration = "Duration is required"
        if (!formData.days) newErrors.days = "Days are required"
        if (!formData.week) newErrors.week = "Week number is required"
        break
      case 3:
        const hasEmptyClass = formData.classes.some((cls) => !cls.name || !cls.size)
        if (hasEmptyClass) newErrors.classes = "All classes must have a name and size"
        if (formData.classes.length === 0) newErrors.classes = "At least one class is required"
        break
      case 4:
        if (!formData.phone_number) {
          newErrors.phone_number = "Phone number is required"
        } else if (!/^\+233\d{9}$/.test(formData.phone_number)) {
          newErrors.phone_number = "Phone number must be in the format +233 followed by 9 digits"
        }
        if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
          newErrors.email = "Invalid email format"
        }
        break
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleNext = () => {
    if (validateCurrentStep()) {
      setCurrentStep((prev) => Math.min(prev + 1, totalSteps))
    }
  }

  const handlePrevious = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1))
  }

  const handleSubmit = async () => {
    if (!validateCurrentStep()) return

    setLoading(true)
    try {
      const agentUrl = process.env.NEXT_PUBLIC_AGENT_URL || "http://localhost:3000"
      // Convert classes array to cls_size object
      const cls_size = formData.classes.reduce((acc, cls) => {
        if (cls.name && cls.size) {
          const key = cls.name.replace(/^Class\s*/, '').trim()
          acc[key] = parseInt(cls.size) || 0
        }
        return acc
      }, {})

      const response = await axios.post(`${agentUrl}/lng/v1/generate-notes`, {
        subject: formData.subject,
        class_level: formData.class_level,
        topic: formData.topic,
        week_ending: formData.week_ending,
        cls_size,
        duration: formData.duration,
        days: formData.days,
        week: formData.week,
        phone_number: formData.phone_number,
        email: formData.email, // Changed to user_email to match backend
        custom_instructions: formData.custom_instructions,
      })

      const fileUrl = response.data.fileUrl || response.data.filePath
      setNotification({
        type: "success",
        message: "Lesson notes generated successfully! Check your WhatsApp and email for the download link.",
        fileUrl,
      })
    } catch (error) {
      let errorMessage = "Failed to generate lesson notes. Please try again."
      if (axios.isAxiosError(error)) {
        errorMessage = error.response?.data?.message || "Server error occurred."
      } else if (error instanceof Error) {
        errorMessage = error.message
      }
      setNotification({
        type: "error",
        message: errorMessage,
      })
    } finally {
      setLoading(false)
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <StepOne
            formData={formData}
            updateFormData={updateFormData}
            errors={errors}
            visibleFieldIndex={visibleFieldIndex}
          />
        )
      case 2:
        return (
          <StepTwo
            formData={formData}
            updateFormData={updateFormData}
            errors={errors}
            visibleFieldIndex={visibleFieldIndex}
          />
        )
      case 3:
        return <StepThree formData={formData} updateFormData={updateFormData} errors={errors} />
      case 4:
        return (
          <StepFour
            formData={formData}
            updateFormData={updateFormData}
            errors={errors}
            visibleFieldIndex={visibleFieldIndex}
          />
        )
      case 5:
        return <StepFive formData={formData} updateFormData={updateFormData} />
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-blue-50 to-purple-50 py-12 px-4 sm:px-6 lg:px-8 flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="max-w-3xl w-full"
      >
        <div className="text-center mb-10">
          <motion.div
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="flex justify-center mb-4"
          >
            <img
              src="/placeholder.svg?height=80&width=80"
              alt="Johnny's Lesson Notes Generator Logo"
              className="h-20 w-20 rounded-full shadow-md"
            />
          </motion.div>
          <motion.h1
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="text-4xl font-extrabold text-gray-900 tracking-tight"
          >
            Johnny's Lesson Notes Generator
          </motion.h1>
          <motion.p
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="text-lg text-gray-600 mt-2"
          >
            Craft professional lesson notes with ease and elegance
          </motion.p>
        </div>

        {notification && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="mb-6"
          >
            <NotificationCard
              type={notification.type}
              message={notification.message}
              fileUrl={notification.fileUrl}
              onClose={() => setNotification(null)}
            />
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="shadow-2xl border-none bg-white/80 backdrop-blur-sm rounded-2xl overflow-hidden">
            <CardHeader className="pb-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-t-2xl">
              <CardTitle className="text-2xl font-semibold">
                Step {currentStep} of {totalSteps}
              </CardTitle>
              <CardDescription className="text-indigo-100">
                {currentStep === 1 && "Start with the core details"}
                {currentStep === 2 && "Add time-related information"}
                {currentStep === 3 && "Define your classes"}
                {currentStep === 4 && "Provide your contact details"}
                {currentStep === 5 && "Include any special instructions"}
              </CardDescription>
              <Progress
                value={progress}
                className="h-2 mt-3 bg-indigo-300/50 [&>div]:bg-gradient-to-r [&>div]:from-indigo-400 [&>div]:to-purple-500"
              />
            </CardHeader>

            <CardContent className="pt-6 px-8">
              <AnimatePresence mode="wait">
                <motion.div
                  key={currentStep}
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -50 }}
                  transition={{ duration: 0.4, ease: "easeInOut" }}
                >
                  {renderStep()}
                </motion.div>
              </AnimatePresence>
            </CardContent>

            <CardFooter className="flex justify-between pt-6 px-8 pb-8 bg-gray-50/50">
              <Button
                variant="outline"
                onClick={handlePrevious}
                disabled={currentStep === 1}
                className="flex items-center gap-2 text-gray-600 border-gray-300 hover:bg-gray-100 transition-colors rounded-lg px-4 py-2"
              >
                <ChevronLeft className="h-5 w-5" />
                Back
              </Button>

              {currentStep < totalSteps ? (
                <Button
                  onClick={handleNext}
                  className="flex items-center gap-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white rounded-lg px-4 py-2 transition-all duration-300"
                >
                  Next
                  <ChevronRight className="h-5 w-5" />
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="flex items-center gap-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white rounded-lg px-4 py-2 transition-all duration-300"
                >
                  {loading ? (
                    <>
                      <span className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full mr-2" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      Generate Notes
                      <Send className="h-5 w-5" />
                    </>
                  )}
                </Button>
              )}
            </CardFooter>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  )
}
