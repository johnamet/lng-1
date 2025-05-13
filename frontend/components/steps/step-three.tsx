"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Plus, Trash2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"

interface StepThreeProps {
  formData: {
    classes: Array<{ name: string; size: string }>
  }
  updateFormData: (data: any) => void
  errors: any
}

export default function StepThree({ formData, updateFormData, errors }: StepThreeProps) {
  const [isAddingClass, setIsAddingClass] = useState(false)

  const handleClassChange = (index: number, field: string, value: string) => {
    const updatedClasses = [...formData.classes]
    updatedClasses[index] = { ...updatedClasses[index], [field]: value }
    updateFormData({ classes: updatedClasses })
  }

  const addClass = () => {
    updateFormData({
      classes: [...formData.classes, { name: "", size: "" }],
    })
    setIsAddingClass(true)
    setTimeout(() => setIsAddingClass(false), 500)
  }

  const removeClass = (index: number) => {
    const updatedClasses = [...formData.classes]
    updatedClasses.splice(index, 1)
    updateFormData({ classes: updatedClasses })
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-4">
        <Label className="text-base font-semibold text-gray-800">Classes</Label>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={addClass}
          className="flex items-center gap-2 border-indigo-300 text-indigo-600 hover:bg-indigo-50 hover:border-indigo-400 rounded-lg transition-all"
        >
          <Plus className="h-4 w-4" />
          Add Class
        </Button>
      </div>

      {errors.classes && <p className="text-sm text-red-500 mb-4">{errors.classes}</p>}

      <AnimatePresence>
        {formData.classes.map((cls, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="bg-white p-4 rounded-lg shadow-sm border border-gray-200"
          >
            <div className="flex justify-between items-center mb-3">
              <h4 className="font-semibold text-gray-800">Class {index + 1}</h4>
              {formData.classes.length > 1 && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeClass(index)}
                  className="h-8 w-8 p-0 text-red-500 hover:text-red-600 hover:bg-red-50 rounded-full transition-all"
                >
                  <Trash2 className="h-4 w-4" />
                  <span className="sr-only">Remove class</span>
                </Button>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor={`class-name-${index}`} className="text-sm font-medium text-gray-700">
                  Class Name
                </Label>
                <Input
                  id={`class-name-${index}`}
                  value={cls.name}
                  onChange={(e) => handleClassChange(index, "name", e.target.value)}
                  placeholder="e.g., Class A"
                  className="rounded-lg border-gray-300 shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`class-size-${index}`} className="text-sm font-medium text-gray-700">
                  Size
                </Label>
                <Input
                  id={`class-size-${index}`}
                  type="number"
                  value={cls.size}
                  onChange={(e) => handleClassChange(index, "size", e.target.value)}
                  placeholder="e.g., 25"
                  className="rounded-lg border-gray-300 shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                />
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {isAddingClass && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="text-sm text-indigo-600 mt-2"
        >
          New class added! Fill in the details.
        </motion.p>
      )}
    </div>
  )
}