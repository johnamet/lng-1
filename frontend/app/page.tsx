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
    classes: [{ name: "Class A", size: "" }], // Dynamic classes
    duration: "",
    days: "",
    week: "",
    phone_number: "+233",
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
            4: 1, // phone_number
            5: 1, // custom_instructions
          }[currentStep] || 0
        return prev < maxFields ? prev + 1 : prev
      })
    }, 400)
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
      // Convert classes array to cls_size object
      const cls_size = formData.classes.reduce((acc, cls) => {
        if (cls.name && cls.size) {
          const key = cls.name.replace(/^Class\s*/, '').trim(); // e.g., "Class A" -> "A"
          acc[key] = parseInt(cls.size) || 0;
        }
        return acc;
      }, {});

      const response = await axios.post('http://localhost:3000/lng/v1/generate-notes', {
        subject: formData.subject,
        class_level: formData.class_level,
        topic: formData.topic,
        week_ending: formData.week_ending,
        cls_size,
        duration: formData.duration,
        days: formData.days,
        week: formData.week,
        phone_number: formData.phone_number,
        custom_instructions: formData.custom_instructions,
      })

      const fileUrl = response.data.fileUrl || response.data.filePath
      setNotification({
        type: "success",
        message: "Lesson notes generated successfully! A WhatsApp notification with the download link has been sent.",
        fileUrl,
      })
    } catch (error) {
      setNotification({
        type: "error",
        message: error.response?.data?.message || "Failed to generate lesson notes. Please try again.",
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
        return <StepFour formData={formData} updateFormData={updateFormData} errors={errors} />
      case 5:
        return <StepFive formData={formData} updateFormData={updateFormData} />
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <img
              src="/placeholder.svg?height=80&width=80"
              alt="Johnny's Lesson Notes Generator Logo"
              className="h-20 w-20"
            />
          </div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Johnny's Lesson Notes Generator</h1>
          <p className="text-xl text-slate-600">Create professional lesson notes easily</p>
        </div>

        {notification && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <NotificationCard
              type={notification.type}
              message={notification.message}
              fileUrl={notification.fileUrl}
              onClose={() => setNotification(null)}
            />
          </motion.div>
        )}

        {!notification && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <Card className="shadow-lg border-0">
              <CardHeader className="pb-4">
                <CardTitle className="text-xl font-semibold">
                  Step {currentStep} of {totalSteps}
                </CardTitle>
                <CardDescription>
                  {currentStep === 1 && "Let's start with the basic information"}
                  {currentStep === 2 && "Now, let's add time-related details"}
                  {currentStep === 3 && "Tell us about your classes"}
                  {currentStep === 4 && "How can we reach you?"}
                  {currentStep === 5 && "Any additional instructions?"}
                </CardDescription>
                <Progress value={progress} className="h-2 mt-2" />
              </CardHeader>

              <CardContent className="pt-2">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentStep}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    {renderStep()}
                  </motion.div>
                </AnimatePresence>
              </CardContent>

              <CardFooter className="flex justify-between pt-6">
                <Button
                  variant="outline"
                  onClick={handlePrevious}
                  disabled={currentStep === 1}
                  className="flex items-center gap-1"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Back
                </Button>

                {currentStep < totalSteps ? (
                  <Button onClick={handleNext} className="flex items-center gap-1">
                    Next
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                ) : (
                  <Button onClick={handleSubmit} disabled={loading} className="flex items-center gap-1">
                    {loading ? (
                      <>
                        <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full mr-1" />
                        Submitting...
                      </>
                    ) : (
                      <>
                        Generate Notes
                        <Send className="h-4 w-4 ml-1" />
                      </>
                    )}
                  </Button>
                )}
              </CardFooter>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  )
}
