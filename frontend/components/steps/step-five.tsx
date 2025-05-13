"use client"

import type React from "react"
import { motion } from "framer-motion"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"

interface StepFiveProps {
  formData: {
    custom_instructions: string
  }
  updateFormData: (data: any) => void
}

export default function StepFive({ formData, updateFormData }: StepFiveProps) {
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const { name, value } = e.target
    updateFormData({ [name]: value })
  }

  const maxLength = 500
  const remainingChars = maxLength - formData.custom_instructions.length

  return (
    <motion.div
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      <div className="space-y-2">
        <Label htmlFor="custom_instructions" className="block text-sm font-medium text-gray-700">
          Custom Instructions (Optional)
        </Label>
        <Textarea
          id="custom_instructions"
          name="custom_instructions"
          value={formData.custom_instructions}
          onChange={handleChange}
          placeholder="e.g., Include examples relevant to Ghanaian culture."
          className="min-h-[150px] rounded-lg border-gray-300 shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
          maxLength={maxLength}
        />
        <div className="flex justify-between text-sm text-muted-foreground mt-1">
          <p>Add any specific requirements or notes for your lesson plan.</p>
          <p>{remainingChars} characters remaining</p>
        </div>
      </div>
    </motion.div>
  )
}